from sqlalchemy.ext.asyncio import AsyncSession


class BaseController:

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session

    def replace_session(
            self,
            session: AsyncSession
    ) -> None:
        """
        This method is used in pattern when controllers are used in other controllers.
        It can be used in order for controllers to share single database session.
        Call this method in constructor of container-controller
        :param session:
        :return:
        """
        self.session = session
