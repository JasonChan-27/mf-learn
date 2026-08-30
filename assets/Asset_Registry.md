# Asset Registry

Version: v2.0 Production Asset Registry

------------------------------------------------------------------------

# 1. Purpose

Asset Registry 是 AI 短剧视觉生产系统中的资产索引层。

核心职责：

-   提供 AI Director 资产决策依据
-   管理 Character Master
-   管理 Environment Master
-   管理 Camera Master
-   管理 Prop Master
-   支持 Image Generation Input
-   支持 Video Generation Input
-   支持 Shot Continuity

Asset Registry 不负责：

-   剧情真相
-   角色人格设定
-   世界观设计
-   导演创作规则
-   镜头拆分规则

上述内容由：

-   Confirmed Script
-   Character Bible
-   World Bible
-   Visual Bible
-   Director Guidelines
-   Production Stage Prompt

负责。

------------------------------------------------------------------------

# 2. Asset Hierarchy

资产层级：

    Asset Registry

    ├── Characters

    ├── Environments

    ├── Cameras

    └── Props

------------------------------------------------------------------------

# 3. Character Assets

Character Asset 用于：

-   角色身份锁定
-   外观一致性
-   毛发/脸型/体型一致性
-   视频连续性
-   情绪和动作参考

------------------------------------------------------------------------

# 3.1 XiaoNan Character Master

Asset ID:

`characters.xiaonan-master`

Asset Type:

Character Master

Purpose:

小南角色唯一视觉参考。

Used For:

-   人物生成
-   情感镜头
-   家庭互动镜头
-   视频连续镜头

Reference Priority:

HIGH

Must Preserve:

-   面部特征
-   发型
-   身材比例
-   年龄感
-   角色整体气质

禁止：

-   改变人物身份
-   重新设计外观
-   改变年龄阶段

------------------------------------------------------------------------

# 3.2 DaPiaoLiang Character Master

Asset ID:

`characters.dapiaoliang-master`

Asset Type:

Character Master

Purpose:

大漂亮角色唯一视觉参考。

Used For:

-   猫咪剧情镜头
-   表情镜头
-   情感互动镜头

Reference Priority:

HIGH

Must Preserve:

-   毛发颜色
-   毛发长度
-   脸型
-   眼睛特征
-   身体比例

禁止：

-   改变猫种特征
-   拟人化身体结构

------------------------------------------------------------------------

# 3.3 XiaoShuai Character Master

Asset ID:

`characters.xiaoshuai-master`

Asset Type:

Character Master

Purpose:

小帅角色唯一视觉参考。

Used For:

-   喜剧镜头
-   反应镜头
-   围观镜头

Must Preserve:

-   猫咪外观
-   体型
-   表情特点

禁止：

-   人类身体动作
-   改变角色身份

------------------------------------------------------------------------

# 3.4 Arno Character Master

Asset ID:

`characters.arno-master`

Asset Type:

Character Master

Purpose:

阿诺角色唯一视觉参考。

Used For:

-   稳重角色镜头
-   保护行为镜头
-   情绪支持镜头

Must Preserve:

-   巨大体型比例
-   长毛特征
-   成熟气质

禁止：

-   缩小体型
-   改变猫咪结构

------------------------------------------------------------------------

# 4. Environment Assets

Environment Asset 用于：

-   空间一致性
-   家具布局一致性
-   光照方向一致性
-   场景连续性

------------------------------------------------------------------------

# 4.1 Home World Master

Asset ID:

`environments.home-world-master`

Purpose:

整个住宅世界观基础。

Used For:

-   全局空间关系
-   场景定位
-   房屋一致性检查

Must Preserve:

-   房屋整体结构
-   空间比例
-   装修风格

------------------------------------------------------------------------

# 4.2 世界观简图

Asset ID:

`environments.世界观简图`

Purpose:

住宅区域关系参考。

Used For:

-   Scene位置判断
-   房间关系确认

------------------------------------------------------------------------

# 4.3 房屋世界观编号

Asset ID:

`environments.房屋世界观编号`

Purpose:

空间编号定位。

Used For:

-   Scene空间选择
-   Camera位置判断

------------------------------------------------------------------------

# 4.4 Entrance Hall Master

Asset ID:

`environments.玄关master2`

Purpose:

玄关固定环境。

Used For:

-   Entrance Scene
-   入门互动
-   出门剧情

Must Preserve:

-   入户门位置
-   鞋柜关系
-   墙体结构
-   客厅连接方向

------------------------------------------------------------------------

# 4.5 Living Room Master

Asset ID:

`environments.客厅master`

Purpose:

客厅固定环境。

Used For:

-   家庭互动
-   猫咪日常剧情

Must Preserve:

-   沙发位置
-   电视区域
-   茶几关系
-   地毯区域

------------------------------------------------------------------------

# 4.6 Dining Room Master

Asset ID:

`environments.餐厅master`

Purpose:

餐厅固定环境。

Used For:

-   吃饭剧情
-   多角色互动

Must Preserve:

-   餐桌位置
-   厨房连接关系

------------------------------------------------------------------------

# 5. Camera Assets

Camera 是强制生产资产。

每个 Shot 必须：

-   明确 Camera Master
-   保持机位连续
-   保持透视关系

禁止：

无 Camera 的 Shot。

------------------------------------------------------------------------

# 5.1 Entrance Hall Camera01

Asset ID:

`cameras.entrance-hall-camera01`

Type:

Camera Master

Purpose:

玄关固定机位。

Visual Language:

-   猫咪视角
-   低机位
-   观察主人视角

Used For:

Entrance相关Shot。

------------------------------------------------------------------------

# 5.2 Living Room Camera06

Asset ID:

`cameras.living-room-camera06`

Type:

Camera Master

Purpose:

客厅固定机位。

Visual Language:

-   低机位
-   猫咪观察视角

Used For:

Living Room相关Shot。

------------------------------------------------------------------------

# 5.3 Dining Room Camera02

Asset ID:

`cameras.dining-room-camera-02`

Purpose:

餐厅固定镜头。

Used For:

Dining Room相关Shot。

------------------------------------------------------------------------

# 5.4 Dining Room Camera05

Asset ID:

`cameras.dining-room-camera-05`

Purpose:

餐厅补充固定镜头。

Used For:

Dining Room相关Shot。

------------------------------------------------------------------------

# 6. Prop Assets

Prop Asset 规则：

只有当道具影响当前 Shot 视觉内容时：

才加入 Asset Decision。

禁止：

因为剧情出现就强制引用。

------------------------------------------------------------------------

# 7. Asset Selection Rules

## Character Selection

选择：

当前 Shot 实际可见角色。

禁止：

引用：

-   不可见角色
-   仅剧情存在角色
-   Previous Shot出现但当前消失角色

------------------------------------------------------------------------

## Environment Selection

选择：

当前 Shot 所在空间。

必须保持：

-   房屋结构
-   家具关系
-   光照方向

------------------------------------------------------------------------

## Camera Selection

每个 Shot 必须：

选择 Camera Master。

Camera 决定：

-   观察角度
-   景别
-   空间关系

------------------------------------------------------------------------

## Prop Selection

如果 Prop：

-   出现在画面
-   影响剧情
-   影响视觉连续

则必须引用。

否则：

禁止增加无关 Prop。

------------------------------------------------------------------------

# 8. Continuity Rules

连续 Shot 必须保持：

Characters:

-   外观
-   体型
-   状态

Environment:

-   空间布局
-   家具位置

Camera:

-   机位
-   视角关系

Props:

-   存在状态

Asset Registry:

负责提供资产。

Shot Continuity Lock:

负责控制连续变化。

------------------------------------------------------------------------

# 9. Production Reference Priority

优先级：

1.  Confirmed Script

2.  Character Bible / World Bible / Visual Bible

3.  Asset Registry

4.  Shot Continuity Lock

5.  Generation Prompt

资产只能服务剧情。

不能改变剧情。
