package org.example;

import java.util.ArrayList;
import java.util.List;

public class DataCleaner {
    public static List<TrackPoint4Alg> cleanData(List<TrackPoint4Alg> trackPoints) {
        List<TrackPoint4Alg> cleanedData = new ArrayList<>();

        for (TrackPoint4Alg point : trackPoints) {
            // 检查字段缺失
            if (point.getLatitude() == Double.NaN || point.getLongitude() == Double.NaN || point.getAltitude() == Double.NaN) {
                continue; // 跳过这个点
            }

            // 检查异常值：经纬度范围、负值、高度异常等
            if (point.getLatitude() < -90 || point.getLatitude() > 90 ||
                    point.getLongitude() < -180 || point.getLongitude() > 180 ||
                    point.getAltitude() < 0 || point.getAltitude() > 10000) {
                continue; // 跳过这个点
            }

            // 检查与航迹不符的值（例如，速度突变或距离异常）
            if (isPointInconsistentWithTrajectory(point, cleanedData)) {
                continue; // 跳过这个点
            }

            // 如果符合条件，加入 cleanedData
            cleanedData.add(point);
        }

        return cleanedData;
    }

    // 判断当前点是否与前面的航迹点不符
    private static boolean isPointInconsistentWithTrajectory(TrackPoint4Alg point, List<TrackPoint4Alg> trajectory) {
        if (trajectory.isEmpty()) {
            return false; // 第一个点无需判断
        }

        // 计算当前点与上一个点的距离或变化速度来判断
        TrackPoint4Alg lastPoint = trajectory.get(trajectory.size() - 1);

        double distance = calculateDistance(lastPoint, point);  // 计算两点之间的地理距离
        if (distance > 1000) { // 比如如果两点距离超过1000米，则视为异常点
            return true;
        }

        // 可以在这里加更多的逻辑，如速度、方向等检查

        return false;
    }

    // 计算两点之间的地理距离（单位：米）
    private static double calculateDistance(TrackPoint4Alg point1, TrackPoint4Alg point2) {
        final double R = 6371e3; // 地球半径（单位：米）

        double lat1 = Math.toRadians(point1.getLatitude());
        double lat2 = Math.toRadians(point2.getLatitude());
        double lon1 = Math.toRadians(point1.getLongitude());
        double lon2 = Math.toRadians(point2.getLongitude());

        double dLat = lat2 - lat1;
        double dLon = lon2 - lon1;

        double a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(lat1) * Math.cos(lat2) *
                        Math.sin(dLon / 2) * Math.sin(dLon / 2);

        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return R * c; // 返回距离（单位：米）
    }
}