from enum import Enum

class StoneType(Enum):
    """
    定義符石的類型，使用枚舉類別來管理所有可能的符石類型。
    """
    CAR: str = "car"           # 汽車符石
    BUS: str = "bus"           # 公車符石
    BIKE: str = "bike"         # 自行車符石
    SCOOTER: str = "scooter"   # 機車符石
    TRAIN: str = "train"       # 火車符石