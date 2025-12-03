from abc import ABC, abstractmethod
import random
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models import Operator, SourceOperatorWeight, Contact
from app.schemas.distribution import DistributionResult


class DistributionStrategy(ABC):
    """Абстрактный класс стратегии распределения контактов."""

    @abstractmethod
    def select_operator(
        self,
        db: Session,
        source_id: int,
        excluded_operator_ids: Optional[List[int]] = None
    ) -> Optional[DistributionResult]:
        pass

    def _get_operator_load(self, db: Session, operator_id: int) -> int:
        """Получить текущую нагрузку оператора."""
        return (
            db.query(func.count(Contact.id))
            .filter(
                Contact.operator_id == operator_id,
                Contact.status.in_(['new', 'in_progress', 'pending'])
            )
            .scalar() or 0
        )


class WeightedDistributionStrategy(DistributionStrategy):
    """Стратегия распределения на основе весов операторов."""

    def get_available_operators(
        self,
        db: Session,
        source_id: int,
        excluded_operator_ids: Optional[List[int]] = None
    ) -> List[SourceOperatorWeight]:
        if excluded_operator_ids is None:
            excluded_operator_ids = []

        query = (
            db.query(SourceOperatorWeight)
            .filter(SourceOperatorWeight.source_id == source_id)
            .options(joinedload(SourceOperatorWeight.operator))
        )

        if excluded_operator_ids:
            query = query.filter(
                SourceOperatorWeight.operator_id.notin_(excluded_operator_ids)
            )

        query = (
            query.join(Operator)
            .filter(Operator.is_active == True)
        )

        return query.all()

    def select_operator(
        self,
        db: Session,
        source_id: int,
        excluded_operator_ids: Optional[List[int]] = None
    ) -> Optional[DistributionResult]:
        """
        Выбрать оператора для распределения контакта на основе
        весов и текущей нагрузки.
        """
        if excluded_operator_ids is None:
            excluded_operator_ids = []

        weights = self.get_available_operators(
            db, source_id, excluded_operator_ids)

        if not weights:
            return None

        available_operators = []

        for weight in weights:
            operator = weight.operator
            current_load = self._get_operator_load(db, operator.id)

            if current_load < operator.load_limit:
                available_operators.append({
                    'operator': operator,
                    'weight': weight.weight,
                    'current_load': current_load,
                    'available_capacity': operator.load_limit - current_load
                })

        if not available_operators:
            return None

        # Вычисляем приоритеты на основе веса и доступной емкости
        operators = []
        priorities = []

        for op_data in available_operators:
            operators.append(op_data['operator'])
            priority = op_data['weight'] * op_data['available_capacity']
            priorities.append(priority)

        total_priority = sum(priorities)
        if total_priority == 0:
            normalized_priorities = [1 / len(priorities)] * len(priorities)
        else:
            normalized_priorities = [p / total_priority for p in priorities]
        selected_operator = random.choices(
            operators,
            weights=normalized_priorities,
            k=1
        )[0]

        operator_weight = next(
            (w.weight for w in weights
             if w.operator_id == selected_operator.id),
            1
        )

        return DistributionResult(
            operator=selected_operator,
            strategy=self.__class__.__name__,
            details={
                'weight': operator_weight,
                'current_load':
                self._get_operator_load(db, selected_operator.id),
                'load_limit': selected_operator.load_limit
            })


class RoundRobinDistributionStrategy(DistributionStrategy):

    def select_operator(
        self,
        db: Session,
        source_id: int,
        excluded_operator_ids: Optional[List[int]] = None
    ) -> Optional[DistributionResult]:
        if excluded_operator_ids is None:
            excluded_operator_ids = []

        operators = (
            db.query(Operator)
            .filter(
                Operator.is_active == True,
                Operator.id.notin_(excluded_operator_ids)
            )
            .order_by(func.coalesce(
                db.query(func.count(Contact.id))
                .filter(
                    Contact.operator_id == Operator.id,
                    Contact.status.in_(['new', 'in_progress', 'pending'])
                )
                .scalar_subquery(),
                0
            ))
            .all()
        )

        if not operators:
            return None

        selected_operator = operators[0]
        current_load = self._get_operator_load(
            db, selected_operator.id)

        if current_load >= selected_operator.load_limit:
            return None

        return DistributionResult(
            operator=selected_operator,
            strategy=self.__class__.__name__,
            details={
                'current_load': current_load,
                'load_limit': selected_operator.load_limit
            }
        )


class DistributionService:
    """Сервис распределения контактов между операторами."""

    def __init__(self, strategy: DistributionStrategy = None):
        self.strategy = strategy or WeightedDistributionStrategy()

    def distribute(
        self,
        db: Session,
        source_id: int,
        excluded_operator_ids: Optional[List[int]] = None
    ) -> DistributionResult:
        result = self.strategy.select_operator(
            db, source_id, excluded_operator_ids)

        if result is None:
            return DistributionResult(
                success=False,
                operator=None,
                error='Не найден доступный оператор'
            )

        result.success = True
        return result

    def set_strategy(self, strategy: DistributionStrategy):
        self.strategy = strategy
