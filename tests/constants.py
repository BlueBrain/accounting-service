"""Constants used for tests."""

import dataclasses
from uuid import UUID


@dataclasses.dataclass(frozen=True)
class UUIDS:
    SYS: UUID
    VLAB: list[UUID]
    PROJ: list[UUID]
    RSV: list[UUID]
    JOB: list[UUID]


UUIDS = UUIDS(
    SYS=UUID("00000000-0000-0000-0000-000000000001"),
    VLAB=[
        UUID("1b3bd3f4-3441-41b0-8fae-83a30c133dc2"),
    ],
    PROJ=[
        UUID("2cb0ea5a-0e6f-4080-a43c-25a4f0dd0ea2"),
        UUID("cccb843e-0b5e-4aed-88b0-6f218a27b6ae"),
    ],
    RSV=[
        UUID("58835fd6-b62d-40bb-97b1-7e071fc35c94"),
        UUID("cd2ea830-1288-482f-b69b-73da9e5da227"),
    ],
    JOB=[
        UUID("923cc386-ae77-44f1-88cd-0cc85cea60b9"),
        UUID("3dade995-fe19-4386-a71a-e24dacf0f0e1"),
        UUID("d2304a0d-f19e-404b-b327-211de0d515b7"),
    ],
)

SYS_ID = str(UUIDS.SYS)
VLAB_ID = str(UUIDS.VLAB[0])
PROJ_ID = str(UUIDS.PROJ[0])
RSV_ID = str(UUIDS.RSV[0])
PROJ_ID_2 = str(UUIDS.PROJ[1])
RSV_ID_2 = str(UUIDS.RSV[1])

KB = 1024
MB = 1024**2
GB = 1024**3
