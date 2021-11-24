import logging
from .base_dao import BaseDAO

from ..models.police import (PoliceTableStatus, PoliceRunHist
                           )
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)


class PoliceDAO(BaseDAO):

    def test(self):
        pass