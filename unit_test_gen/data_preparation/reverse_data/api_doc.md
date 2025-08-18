# 文件名：DataCleaner.java
## 总体功能
该类提供数据清洗功能，主要用于处理轨迹点数据。它会过滤掉字段缺失、异常值以及与航迹不符的轨迹点，最终返回清洗后的轨迹点列表。
## 接口说明
### cleanData
*函数功能*：清洗轨迹点数据，去除不符合要求的点。
*函数参数*：
    * `trackPoints`：`List<TrackPoint4Alg>`类型，表示待清洗的轨迹点列表。
*返回值*：`List<TrackPoint4Alg>`，表示清洗后的轨迹点列表。
*异常*：无

### isPointInconsistentWithTrajectory
*函数功能*：判断当前点是否与前面的航迹点不符。
*函数参数*：
    * `point`：`TrackPoint4Alg`类型，表示当前要判断的轨迹点。
    * `trajectory`：`List<TrackPoint4Alg>`类型，表示前面的航迹点列表。
*返回值*：`boolean`，如果当前点与前面的航迹点不符则返回`true`，否则返回`false`。
*异常*：无

### calculateDistance
*函数功能*：计算两点之间的地理距离。
*函数参数*：
    * `point1`：`TrackPoint4Alg`类型，表示第一个轨迹点。
    * `point2`：`TrackPoint4Alg`类型，表示第二个轨迹点。
*返回值*：`double`，表示两点之间的地理距离（单位：米）。
*异常*：无

# 文件名：FindMinDistanceXYAndZ.java
## 总体功能
该类用于计算两个无人机（UAV）轨迹点之间的最小水平距离和最小垂直距离。它包含一个`TrackPoint`类，用于表示轨迹点，以及一个`findMinDistances`方法，用于计算最小距离。此外，还包含辅助类`Pair`和`Result`，用于存储计算结果。
## 接口说明
### 函数名：haversineDistance
*函数功能*  
计算两个地理坐标点之间的水平距离，使用哈弗赛因公式。
*函数参数*  
- `double lat1`：第一个点的纬度。
- `double lon1`：第一个点的经度。
- `double lat2`：第二个点的纬度。
- `double lon2`：第二个点的经度。
*返回值*  
- `double`：两个点之间的水平距离，单位为米。
*异常*  
- 无

### 函数名：findMinDistances
*函数功能*  
计算两个无人机轨迹点列表之间的最小水平距离和最小垂直距离。
*函数参数*  
- `List<TrackPoint> uavA`：第一个无人机的轨迹点列表。
- `List<TrackPoint> uavB`：第二个无人机的轨迹点列表。
*返回值*  
- `Result`：包含最小水平距离、最小垂直距离以及对应的轨迹点对。
*异常*  
- 无

### 函数名：TrackPoint（构造函数）
*函数功能*  
创建一个轨迹点对象。
*函数参数*  
- `String time`：轨迹点的时间戳。
- `double latitude`：轨迹点的纬度。
- `double longitude`：轨迹点的经度。
- `double altitude`：轨迹点的海拔高度。
*返回值*  
- 无
*异常*  
- 无

### 函数名：Pair（构造函数）
*函数功能*  
创建一个轨迹点对对象。
*函数参数*  
- `TrackPoint pointA`：第一个轨迹点。
- `TrackPoint pointB`：第二个轨迹点。
*返回值*  
- 无
*异常*  
- 无

### 函数名：Result（构造函数）
*函数功能*  
创建一个结果对象，包含最小水平距离、最小垂直距离以及对应的轨迹点对。
*函数参数*  
- `List<Pair> horizontalPairs`：最小水平距离对应的轨迹点对列表。
- `double minHorizontalDistance`：最小水平距离。
- `List<Pair> verticalPairs`：最小垂直距离对应的轨迹点对列表。
- `double minVerticalDistance`：最小垂直距离。
*返回值*  
- 无
*异常*  
- 无

# 文件名
FlightPathConsistencyCheck.java

## 总体功能
该类提供无人机飞行路径一致性检查的功能。它包含多个静态方法，用于计算两点之间的水平距离（Haversine 公式）、垂直距离（高度差）、检查无人机当前位置是否满足阈值条件，以及从 CSV 文件中读取航点数据。此外，还包含一个内部类 `UAVPositionCheck`，用于执行一些与无人机位置相关的计算，如地理坐标与笛卡尔坐标之间的转换、计算垂足位置等。

## 接口说明

### UAVPositionCheck.haversine
*函数功能*  
计算两点之间的 Haversine 距离，即地球表面上两点之间的最短距离。
*函数参数*  
- `lat1`：第一个点的纬度（度）。
- `lon1`：第一个点的经度（度）。
- `lat2`：第二个点的纬度（度）。
- `lon2`：第二个点的经度（度）。
*返回值*  
两点之间的 Haversine 距离（米）。
*异常*  
无

### UAVPositionCheck.geodeticToCartesian
*函数功能*  
将地理坐标（纬度、经度、高度）转换为笛卡尔坐标（x、y、z）。
*函数参数*  
- `lat`：纬度（度）。
- `lon`：经度（度）。
- `h`：高度（米）。
*返回值*  
一个包含三个元素的数组，分别表示 x、y、z 坐标。
*异常*  
无

### UAVPositionCheck.cartesianToGeodetic
*函数功能*  
将笛卡尔坐标（x、y、z）转换回地理坐标（纬度、经度、高度）。
*函数参数*  
- `x`：x 坐标。
- `y`：y 坐标。
- `z`：z 坐标。
*返回值*  
一个包含三个元素的数组，分别表示纬度、经度、高度。
*异常*  
无

### UAVPositionCheck.calculateFootPoint
*函数功能*  
计算从点 P 到线段 AB 的垂足位置。
*函数参数*  
- `latP`：点 P 的纬度（度）。
- `lonP`：点 P 的经度（度）。
- `hP`：点 P 的高度（米）。
- `latA`：点 A 的纬度（度）。
- `lonA`：点 A 的经度（度）。
- `hA`：点 A 的高度（米）。
- `latB`：点 B 的纬度（度）。
- `lonB`：点 B 的经度（度）。
- `hB`：点 B 的高度（米）。
*返回值*  
一个包含三个元素的数组，表示垂足的纬度、经度、高度。
*异常*  
无

### FlightPathConsistencyCheck.haversine
*函数功能*  
计算两点之间的水平距离，使用 Haversine 公式。
*函数参数*  
- `lon1`：第一个点的经度（度）。
- `lat1`：第一个点的纬度（度）。
- `lon2`：第二个点的经度（度）。
- `lat2`：第二个点的纬度（度）。
*返回值*  
两点之间的水平距离（米）。
*异常*  
无

### FlightPathConsistencyCheck.verticalDistance
*函数功能*  
计算两点之间的垂直距离，即高度差。
*函数参数*  
- `alt1`：第一个点的高度（米）。
- `alt2`：第二个点的高度（米）。
*返回值*  
两点之间的垂直距离（米）。
*异常*  
无

### FlightPathConsistencyCheck.checkThreshold
*函数功能*  
检查无人机当前位置是否满足给定的水平和垂直阈值条件。
*函数参数*  
- `currentPos`：无人机当前位置，包含经度、纬度、高度的数组。
- `waypoints`：航点列表，每个航点是一个包含经度、纬度、高度的数组。
- `horizontalThreshold`：水平距离阈值（米）。
- `verticalThreshold`：垂直距离阈值（米）。
*返回值*  
如果无人机当前位置满足任一阈值条件，则返回 `true`；否则返回 `false`。
*异常*  
无

### FlightPathConsistencyCheck.readCSV
*函数功能*  
从 CSV 文件中读取航点数据。
*函数参数*  
- `filePath`：CSV 文件路径。
*返回值*  
一个包含航点数据的列表，每个航点是一个包含经度、纬度、高度的数组。
*异常*  
- `IOException`：如果文件读取过程中发生错误，则抛出此异常。

# interpolation.java
## 总体功能
该类提供了一种方法来对两条轨迹进行时间对齐。它通过在轨迹B中找到与轨迹A中每个点时间最接近的两个点，然后使用这两个点对轨迹B进行线性插值，从而计算出轨迹A和插值后的轨迹B之间的空间距离。
## 接口说明
### alignTrajectoryBToA
*函数功能*  
将轨迹B对齐到轨迹A的时间线上，通过在轨迹B中找到与轨迹A中每个点时间最接近的两个点，然后进行线性插值，计算出轨迹A和插值后的轨迹B之间的空间距离。
*函数参数*  
- `List<TrackPoint4Alg> trajectoryA`：轨迹A的点列表。
- `List<TrackPoint4Alg> trajectoryB`：轨迹B的点列表。
*返回值*  
无返回值。
*异常*  
无异常。

### findClosestPointBefore
*函数功能*  
在轨迹B中找到时间小于指定点时间的最接近的点。
*函数参数*  
- `TrackPoint4Alg pointA`：指定的点。
- `List<TrackPoint4Alg> trajectoryB`：轨迹B的点列表。
*返回值*  
返回轨迹B中时间小于指定点时间的最接近的点，如果不存在则返回`null`。
*异常*  
无异常。

### findClosestPointAfter
*函数功能*  
在轨迹B中找到时间大于指定点时间的最接近的点。
*函数参数*  
- `TrackPoint4Alg pointA`：指定的点。
- `List<TrackPoint4Alg> trajectoryB`：轨迹B的点列表。
*返回值*  
返回轨迹B中时间大于指定点时间的最接近的点，如果不存在则返回`null`。
*异常*  
无异常。

### linearInterpolate
*函数功能*  
对两个点进行线性插值，获取在指定时间上的坐标。
*函数参数*  
- `TrackPoint4Alg p1`：第一个点。
- `TrackPoint4Alg p2`：第二个点。
- `long targetTime`：目标时间。
*返回值*  
返回插值后的点。
*异常*  
无异常。

### calculateDistance
*函数功能*  
计算两个点之间的空间距离。
*函数参数*  
- `TrackPoint4Alg p1`：第一个点。
- `TrackPoint4Alg p2`：第二个点。
*返回值*  
返回两个点之间的空间距离。
*异常*  
无异常。

# 文件名
minDistanceCal.java

## 总体功能
该类提供了一组方法用于计算航迹点之间的距离，包括球面距离和三维距离，并能够计算两条航迹之间的最小距离和平均距离。

## 接口说明
### haversineDistance
*函数功能*  
计算两个地理坐标点之间的球面距离，单位为米。
*函数参数*  
- `double lon1`：第一个点的经度。
- `double lat1`：第一个点的纬度。
- `double lon2`：第二个点的经度。
- `double lat2`：第二个点的纬度。
*返回值*  
两个点之间的球面距离，单位为米。
*异常*  
无

### calculate3dDistance
*函数功能*  
计算两个航迹点之间的三维距离，考虑了经度、纬度和高度。
*函数参数*  
- `TrackPoint p1`：第一个航迹点。
- `TrackPoint p2`：第二个航迹点。
*返回值*  
两个点之间的三维距离，单位为米。
*异常*  
无

### minDistanceCal
*函数功能*  
计算两条航迹之间的最小距离和平均距离，并返回相关信息。
*函数参数*  
- `List<TrackPoint> trackA`：第一条航迹的点列表。
- `List<TrackPoint> trackB`：第二条航迹的点列表。
*返回值*  
一个`Result`对象，包含最小距离、平均距离以及对应的最近点。
*异常*  
无

### TrackPoint
*函数功能*  
表示一个航迹点，包含时间、纬度、经度和高度信息。
*函数参数*  
- `String time`：时间戳。
- `double latitude`：纬度。
- `double longitude`：经度。
- `double altitude`：高度。
*返回值*  
无
*异常*  
无

### Result
*函数功能*  
表示计算结果，包含最小距离、平均距离以及对应的最近点。
*函数参数*  
- `double minDistance`：最小距离。
- `double averageDistance`：平均距离。
- `TrackPoint closestPoint1`：第一条航迹的最近点。
- `TrackPoint closestPoint2`：第二条航迹的最近点。
*返回值*  
无
*异常*  
无

# TrackPoint4Alg 类接口文档

## 总体功能
`TrackPoint4Alg` 类用于表示一个轨迹点的详细信息，包括设备名称、时间戳、经纬度、高度、速度和加速度等数据。该类提供了构造方法用于初始化轨迹点数据，以及 Getter 和 Setter 方法用于访问和修改各个属性值，还重写了 `toString` 方法以便于打印对象信息。

## 接口说明

### 构造方法
*函数功能*  
构造一个轨迹点对象，初始化其设备名称、时间戳、经纬度、高度、速度和加速度等属性。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| name | String | 设备名称 |
| timestamp | long | 时间戳 |
| longitude | double | 经度 |
| latitude | double | 纬度 |
| altitude | double | 高度 |
| northVelocity | double | 北向速度 |
| eastVelocity | double | 东向速度 |
| downVelocity | double | 地向速度 |
| northAcceleration | double | 北向加速度 |
| eastAcceleration | double | 东向加速度 |
| downAcceleration | double | 地向加速度 |
*返回值*  
无
*异常*  
无

### Getter 和 Setter 方法
#### getName
*函数功能*  
获取设备名称。
*函数参数*  
无
*返回值*  
返回设备名称，类型为 `String`。
*异常*  
无

#### setName
*函数功能*  
设置设备名称。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| name | String | 设备名称 |
*返回值*  
无
*异常*  
无

#### getTimestamp
*函数功能*  
获取时间戳。
*函数参数*  
无
*返回值*  
返回时间戳，类型为 `long`。
*异常*  
无

#### setTimestamp
*函数功能*  
设置时间戳。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| timestamp | long | 时间戳 |
*返回值*  
无
*异常*  
无

#### getLongitude
*函数功能*  
获取经度。
*函数参数*  
无
*返回值*  
返回经度，类型为 `double`。
*异常*  
无

#### setLongitude
*函数功能*  
设置经度。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| longitude | double | 经度 |
*返回值*  
无
*异常*  
无

#### getLatitude
*函数功能*  
获取纬度。
*函数参数*  
无
*返回值*  
返回纬度，类型为 `double`。
*异常*  
无

#### setLatitude
*函数功能*  
设置纬度。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| latitude | double | 纬度 |
*返回值*  
无
*异常*  
无

#### getAltitude
*函数功能*  
获取高度。
*函数参数*  
无
*返回值*  
返回高度，类型为 `double`。
*异常*  
无

#### setAltitude
*函数功能*  
设置高度。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| altitude | double | 高度 |
*返回值*  
无
*异常*  
无

#### getNorthVelocity
*函数功能*  
获取北向速度。
*函数参数*  
无
*返回值*  
返回北向速度，类型为 `double`。
*异常*  
无

#### setNorthVelocity
*函数功能*  
设置北向速度。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| northVelocity | double | 北向速度 |
*返回值*  
无
*异常*  
无

#### getEastVelocity
*函数功能*  
获取东向速度。
*函数参数*  
无
*返回值*  
返回东向速度，类型为 `double`。
*异常*  
无

#### setEastVelocity
*函数功能*  
设置东向速度。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| eastVelocity | double | 东向速度 |
*返回值*  
无
*异常*  
无

#### getDownVelocity
*函数功能*  
获取地向速度。
*函数参数*  
无
*返回值*  
返回地向速度，类型为 `double`。
*异常*  
无

#### setDownVelocity
*函数功能*  
设置地向速度。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| downVelocity | double | 地向速度 |
*返回值*  
无
*异常*  
无

#### getNorthAcceleration
*函数功能*  
获取北向加速度。
*函数参数*  
无
*返回值*  
返回北向加速度，类型为 `double`。
*异常*  
无

#### setNorthAcceleration
*函数功能*  
设置北向加速度。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| northAcceleration | double | 北向加速度 |
*返回值*  
无
*异常*  
无

#### getEastAcceleration
*函数功能*  
获取东向加速度。
*函数参数*  
无
*返回值*  
返回东向加速度，类型为 `double`。
*异常*  
无

#### setEastAcceleration
*函数功能*  
设置东向加速度。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| eastAcceleration | double | 东向加速度 |
*返回值*  
无
*异常*  
无

#### getDownAcceleration
*函数功能*  
获取地向加速度。
*函数参数*  
无
*返回值*  
返回地向加速度，类型为 `double`。
*异常*  
无

#### setDownAcceleration
*函数功能*  
设置地向加速度。
*函数参数*  
| 参数名称 | 参数类型 | 参数描述 |
| --- | --- | --- |
| downAcceleration | double | 地向加速度 |
*返回值*  
无
*异常*  
无

### toString
*函数功能*  
重写 `toString` 方法，返回轨迹点对象的详细信息，包括设备名称、时间戳、经纬度、高度、速度和加速度等。
*函数参数*  
无
*返回值*  
返回轨迹点对象的详细信息，类型为 `String`。
*异常*  
无

# 文件名
TrackPredMotionEquation.java

## 总体功能
该类用于预测无人机的未来轨迹。它基于当前状态（包括时间戳、经纬度、高度、速度和加速度）和预测参数（预测时间和时间步长），通过物理运动方程计算未来轨迹，并提供打印轨迹的功能。

## 接口说明
### predictTrajectory
*函数功能*
根据无人机的当前状态和预测参数，预测其未来轨迹。轨迹以时间戳、经度、纬度和高度的形式返回。
*函数参数*
- `currentState`：`double[]`，无人机的当前状态，包含以下元素：
  - `timestamp`：时间戳（单位：秒）
  - `longitude`：经度（单位：度）
  - `latitude`：纬度（单位：度）
  - `altitude`：高度（单位：米）
  - `vNorth`：北向速度（单位：米/秒）
  - `vEast`：东向速度（单位：米/秒）
  - `vDown`：下向速度（单位：米/秒）
  - `aNorth`：北向加速度（单位：米/秒²）
  - `aEast`：东向加速度（单位：米/秒²）
  - `aDown`：下向加速度（单位：米/秒²）
- `predictionTime`：`double`，预测时间（单位：秒）
- `timeStep`：`double`，时间步长（单位：秒）
*返回值*
- `List<double[]>`，预测轨迹的列表，每个轨迹点包含以下元素：
  - `timestamp`：时间戳（单位：秒）
  - `longitude`：经度（单位：度）
  - `latitude`：纬度（单位：度）
  - `altitude`：高度（单位：米）
*异常*
- 无

### printTrajectory
*函数功能*
打印预测的轨迹，格式为时间戳、经度、纬度和高度。
*函数参数*
- `trajectory`：`List<double[]>`，预测的轨迹
*返回值*
- 无
*异常*
- 无

# 文件名
TrajectoryPrediction.java

## 总体功能
该类提供了一个基于历史轨迹数据预测未来轨迹的功能。它通过最小二乘法拟合历史轨迹数据中的纬度、经度和高度，然后利用拟合的多项式模型预测未来一段时间内的轨迹点。

## 接口说明
### predictTrajectory
*函数功能*  
根据历史轨迹数据预测未来一段时间内的轨迹。该函数首先解析历史数据的时间戳，将其转换为相对于最后一个时间点的相对时间（单位为秒）。然后，分别对纬度、经度和高度进行多项式拟合，最后利用拟合的多项式模型预测未来一段时间内的轨迹点。
*函数参数*  
- `historyData`：`List<Record>`类型，表示历史轨迹数据，每个`Record`对象包含时间戳、纬度、经度和高度等信息。
- `futurePeriod`：`int`类型，表示预测未来的时间长度（单位为秒），但目前代码中未使用该参数，固定预测未来60秒的轨迹。
*返回值*  
返回一个`List<Record>`，表示预测的未来轨迹点，每个`Record`对象包含预测的时间戳、纬度、经度和高度。
*异常*  
可能抛出`ParseException`，表示在解析时间戳时发生错误。

### fitPolynomial
*函数功能*  
使用最小二乘法拟合给定数据点的多项式模型。该函数构造了设计矩阵X和目标向量y，然后通过计算XT * X和XT * y，最终使用高斯消去法解线性方程组，得到多项式的系数。
*函数参数*  
- `x`：`List<Double>`类型，表示自变量数据点。
- `y`：`List<Double>`类型，表示因变量数据点。
- `degree`：`int`类型，表示拟合多项式的最高次数。
*返回值*  
返回一个`double[]`，表示拟合多项式的系数，从最高次项到常数项。
*异常*  
无

### solveLinearSystem
*函数功能*  
使用高斯消去法解线性方程组。该函数通过行交换将矩阵A转换为上三角矩阵，然后通过回代求解线性方程组的解。
*函数参数*  
- `A`：`double[][]`类型，表示系数矩阵。
- `b`：`double[]`类型，表示目标向量。
*返回值*  
返回一个`double[]`，表示线性方程组的解。
*异常*  
无

### evaluatePolynomial
*函数功能*  
计算多项式在给定点的值。该函数利用霍纳法则高效地计算多项式的值。
*函数参数*  
- `coef`：`double[]`类型，表示多项式的系数，从最高次项到常数项。
- `x`：`double`类型，表示计算多项式值的点。
*返回值*  
返回一个`double`，表示多项式在给定点的值。
*异常*  
无

### transposeMatrix
*函数功能*  
计算矩阵的转置。该函数将矩阵的行和列互换，生成转置矩阵。
*函数参数*  
- `matrix`：`double[][]`类型，表示需要转置的矩阵。
*返回值*  
返回一个`double[][]`，表示转置后的矩阵。
*异常*  
无

### multiplyMatrices
*函数功能*  
计算两个矩阵的乘积。该函数按照矩阵乘法的规则，计算两个矩阵的乘积。
*函数参数*  
- `A`：`double[][]`类型，表示第一个矩阵。
- `B`：`double[][]`类型，表示第二个矩阵。
*返回值*  
返回一个`double[][]`，表示两个矩阵的乘积。
*异常*  
无

# 文件名
TrajectoryPredictionV1.java

## 总体功能
该类提供了轨迹预测的功能，通过指定拟合方式，对给定的二维数据点进行拟合，返回对应的多项式函数。支持线性拟合和二次多项式拟合。

## 接口说明
### fitTrajectory
*函数功能*  
根据指定的拟合方式对给定的二维数据点进行拟合，返回对应的多项式函数。支持线性拟合（拟合类型为1）和二次多项式拟合（拟合类型为2）。
*函数参数*  
- `double[] x`：数据点的横坐标数组。
- `double[] y`：数据点的纵坐标数组。
- `int fittingType`：拟合方式，1表示线性拟合，2表示二次多项式拟合。
*返回值*  
返回一个`PolynomialFunction`对象，表示拟合后的多项式函数。
*异常*  
- `IllegalArgumentException`：当`fittingType`不是1或2时抛出此异常，提示不支持的拟合类型。

# 文件名：TrajectoryVisualization.java
## 总体功能
该类用于轨迹可视化的功能实现，包括从 CSV 文件读取数据、生成示例数据、保存静态图像以及绘制轨迹面板等。它通过静态方法和内部类 TrajectoryPanel 实现了轨迹数据的读取、处理和可视化。

## 接口说明
### readCsvData
*函数功能*  
从指定的 CSV 文件路径读取数据，如果文件不存在则生成示例数据。数据包括时间、经度、纬度和高度，同时会添加模拟的测量数据（带噪声）。
*函数参数*  
- `String filePath`：CSV 文件的路径。
*返回值*  
- `boolean`：如果成功读取或生成数据则返回 `true`，否则返回 `false`。
*异常*  
- `IOException`：如果在读取文件时发生输入输出异常。

### generateSampleData
*函数功能*  
生成示例数据，用于在无法读取 CSV 文件时提供默认数据。生成的数据包括时间、经度、纬度和高度，同时会添加模拟的测量数据（带噪声）。
*函数参数*  
无。
*返回值*  
无。
*异常*  
无。

### saveFrames
*函数功能*  
保存轨迹面板的每一帧为静态图像。根据传入的面板、宽度、高度和文件前缀，将每一帧绘制为 BufferedImage 并保存为 PNG 文件。
*函数参数*  
- `TrajectoryPanel panel`：轨迹面板实例。
- `int width`：图像宽度。
- `int height`：图像高度。
- `String filePrefix`：保存文件的前缀。
*返回值*  
无。
*异常*  
- `IOException`：如果在保存图像时发生输入输出异常。

### TrajectoryPanel
*函数功能*  
内部类，用于绘制轨迹面板。面板上会绘制真实轨迹、测量数据和未来预测轨迹，并且可以根据当前帧数动态更新显示内容。
*函数参数*  
- `int width`：面板宽度。
- `int height`：面板高度。
*返回值*  
无。
*异常*  
无。

#### setFrame
*函数功能*  
设置当前帧数，并根据当前帧更新未来预测数据。同时触发面板的重绘。
*函数参数*  
- `int frame`：当前帧数。
*返回值*  
无。
*异常*  
无。

#### paintComponent
*函数功能*  
重写 JPanel 的 paintComponent 方法，用于绘制面板内容。绘制内容包括背景、网格、真实轨迹、测量数据和未来预测轨迹。
*函数参数*  
- `Graphics g`：绘图上下文。
*返回值*  
无。
*异常*  
无。

#### drawPoint
*函数功能*  
在面板上绘制一个点，根据传入的位置、坐标范围和颜色进行绘制。
*函数参数*  
- `Graphics2D g2d`：绘图上下文。
- `double[] pos`：点的位置，包含经度、纬度和高度。
- `double lonMin`：经度最小值。
- `double lonMax`：经度最大值。
- `double latMin`：纬度最小值。
- `double latMax`：纬度最大值。
- `Color color`：点的颜色。
*返回值*  
无。
*异常*  
无。

# 文件名：UAVWaypointAdjustment.java

## 总体功能
该类用于调整无人机的航迹点高度，以避免无人机之间的高度冲突。它包含一个内部类 `TrackPoint` 用于存储航迹点的时间、纬度、经度和高度信息，以及一个静态方法 `adjustUAVWaypoints` 用于根据给定的高度阈值调整无人机的航迹点高度。

## 接口说明

### 函数名：adjustUAVWaypoints
*函数功能*  
根据给定的高度阈值调整无人机的航迹点高度，以避免无人机之间的高度冲突。该方法会根据两个无人机的航迹点高度差，调整高度较高者的高度，使其满足高度差阈值要求。调整策略分为三个阶段：前25秒逐渐提高高度，中间10秒维持调整后的高度，最后25秒逐渐回到原来的高度。

*函数参数*  
- `altitudeThreshold`：高度阈值，表示两个无人机航迹点之间的最小高度差。
- `uavAPoints`：无人机A的航迹点列表。
- `uavBPoints`：无人机B的航迹点列表。

*返回值*  
返回一个包含两个列表的数组，第一个列表为调整后的无人机A的航迹点列表，第二个列表为调整后的无人机B的航迹点列表。

*异常*  
无

