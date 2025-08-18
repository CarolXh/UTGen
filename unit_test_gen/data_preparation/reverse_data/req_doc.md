# 项目背景
这个项目涉及到无人机轨迹数据的处理与分析，主要功能包括数据清洗、轨迹对齐、距离计算、路径一致性检查以及轨迹预测等。项目的目标是确保无人机的飞行路径准确、安全，并对轨迹数据进行有效的处理和可视化，以便进一步分析与研究。

# 项目业务流程
以下是该项目的业务流程：
1. **数据输入**：通过CSV文件或其他方式输入无人机的原始轨迹数据。
2. **数据清洗**：使用`DataCleaner.cleanData`方法去除轨迹点数据中的噪声点和异常点。
3. **轨迹对齐**：使用`interpolation.alignTrajectoryBToA`方法对轨迹数据进行时间对齐。
4. **距离计算**：通过`FindMinDistanceXYAndZ.findMinDistances`和`minDistanceCal.minDistanceCal`等方法计算轨迹点之间的距离。
5. **路径一致性检查**：利用`FlightPathConsistencyCheck`类的相关方法检查无人机当前位置是否满足阈值条件，确保飞行路径的一致性。
6. **轨迹预测**：使用`TrajectoryPrediction.predictTrajectory`和`TrajectoryPredictionV1.predictTrajectory`等方法预测无人机的未来轨迹。
7. **航迹点调整**：通过`UAVWaypointAdjustment.adjustUAVWaypoints`方法根据高度阈值调整无人机的航迹点高度。
8. **轨迹可视化**：使用`TrajectoryVisualization.readCsvData`从CSV文件读取数据，然后通过`TrajectoryVisualization.saveFrames`方法保存轨迹可视化结果。

# 功能需求
## CalculateDistances
*用例描述*：计算无人机轨迹点之间的最小水平距离和最小垂直距离。
*条件*：提供两个无人机的轨迹点列表。
*接口说明*：
    - `haversineDistance`：
        - 计算两个地理坐标点之间的水平距离。
        - 参数：第一个点的纬度和经度、第二个点的纬度和经度。
        - 返回值：两个点之间的水平距离（单位：米）。
    - `findMinDistances`：
        - 计算两个无人机轨迹点列表之间的最小水平距离和最小垂直距离。
        - 参数：两个无人机的轨迹点列表。
        - 返回值：包含最小水平距离、最小垂直距离以及对应的轨迹点对的`Result`对象。

## DataCleaning
*用例描述*：对无人机轨迹点数据进行清洗，去除不满足要求的点。
*条件*：提供待清洗的轨迹点列表。
*接口说明*：
    - `cleanData`：
        - 清洗轨迹点数据，去除字段缺失、异常值以及与航迹不符的点。
        - 参数：待清洗的轨迹点列表。
        - 返回值：清洗后的轨迹点列表。
    - `isPointInconsistentWithTrajectory`：
        - 判断当前点是否与前面的航迹点不符。
        - 参数：当前要判断的轨迹点和前面的航迹点列表。
        - 返回值：如果当前点与前面的航迹点不符则返回`true`，否则返回`false`。

## FlightPathConsistencyChecking
*用例描述*：检查无人机的飞行路径是否一致，包括检查水平和垂直方向上的满足程度。
*条件*：提供无人机的当前位置、航点列表、水平阈值和垂直阈值。
*接口说明*：
    - `checkThreshold`：
        - 检查无人机当前位置是否满足给定的水平和垂直阈值条件。
        - 参数：无人机当前位置、航点列表、水平距离阈值、垂直距离阈值。
        - 返回值：如果无人机当前位置满足任一阈值条件，则返回`true`；否则返回`false`。
    - `readCSV`：
        - 从CSV文件中读取航点数据。
        - 参数：CSV文件路径。
        - 返回值：包含航点数据的列表。
    - `haversine`：
        - 计算两点之间的水平距离，使用Haversine公式。
        - 参数：第一个点的纬度和经度、第二个点的纬度和经度。
        - 返回值：两点之间的水平距离。
    - `verticalDistance`：
        - 计算两点之间的垂直距离，即高度差。
        - 参数：第一个点的高度和第二个点的高度。
        - 返回值：两点之间的垂直距离。
    - `geodeticToCartesian`：
        - 将地理坐标转换为笛卡尔坐标。
        - 参数：纬度、经度、高度。
        - 返回值：笛卡尔坐标。
    - `cartesianToGeodetic`：
        - 将笛卡尔坐标转换为地理坐标。
        - 参数：x、y、z坐标。
        - 返回值：地理坐标。
    - `calculateFootPoint`：
        - 计算从点P到线段AB的垂足位置。
        - 参数：点P和线段AB的坐标。
        - 返回值：垂足的坐标。

## PredictTrajectory
*用例描述*：根据无人机的当前状态预测其未来轨迹。
*条件*：提供无人机的当前状态、预测时间和时间步长。
*接口说明*：
    - `predictTrajectory`：
        - 根据无人机的当前状态和预测参数预测其未来轨迹。
        - 参数：无人机的当前状态、预测时间、时间步长。
        - 返回值：预测轨迹的列表。

## TrajectoryAlignment
*用例描述*：将轨迹B对齐到轨迹A的时间线上。
*条件*：提供轨迹A和轨迹B的点列表。
*接口说明*：
    - `alignTrajectoryBToA`：
        - 将轨迹B对齐到轨迹A的时间线上。
        - 参数：轨迹A和轨迹B的点列表。
        - 返回值：无返回值。
    - `findClosestPointBefore`：
        - 在轨迹B中找到时间小于指定点时间的最接近的点。
        - 参数：指定的点和轨迹B