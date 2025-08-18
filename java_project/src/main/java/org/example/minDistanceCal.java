package org.example;

import java.util.ArrayList;
import java.util.List;

public class minDistanceCal {

    static final double EARTH_RADIUS = 6371000; // 地球半径，单位：米

    // 计算球面距离（单位：米）
    public static double haversineDistance(double lon1, double lat1, double lon2, double lat2) {
        lon1 = Math.toRadians(lon1);
        lat1 = Math.toRadians(lat1);
        lon2 = Math.toRadians(lon2);
        lat2 = Math.toRadians(lat2);

        double dlon = lon2 - lon1;
        double dlat = lat2 - lat1;
        double a = Math.sin(dlat / 2) * Math.sin(dlat / 2) +
                   Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) * Math.sin(dlon / 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return EARTH_RADIUS * c;
    }

    // 计算三维距离
    public static double calculate3dDistance(TrackPoint p1, TrackPoint p2) {
        double lon1 = p1.longitude, lat1 = p1.latitude, alt1 = p1.altitude;
        double lon2 = p2.longitude, lat2 = p2.latitude, alt2 = p2.altitude;

        double surfaceDistance = haversineDistance(lon1, lat1, lon2, lat2);
        double heightDiff = Math.abs(alt1 - alt2);

        return Math.sqrt(surfaceDistance * surfaceDistance + heightDiff * heightDiff);
    }

    // 生成均匀分布的航迹点
    // public static List<double[]> generateTrajectory(double[] start, double[] end, int numPoints) {
    //     List<double[]> trajectory = new ArrayList<>();
    //     double lon1 = start[0], lat1 = start[1], alt1 = start[2];
    //     double lon2 = end[0], lat2 = end[1], alt2 = end[2];

    //     for (int i = 0; i < numPoints; i++) {
    //         double lon = lon1 + i * (lon2 - lon1) / (numPoints - 1);
    //         double lat = lat1 + i * (lat2 - lat1) / (numPoints - 1);
    //         double alt = alt1 + i * (alt2 - alt1) / (numPoints - 1);
    //         trajectory.add(new double[]{lon, lat, alt});
    //     }

    //     return trajectory;
    // }

    public static Result minDistanceCal(List<TrackPoint> trackA, List<TrackPoint> trackB) {
        // 计算同一时间两两对应航迹点的距离
        double minDistance = Double.MAX_VALUE;
        double averageDistance = 0.0;
        TrackPoint closestPoint1 = null;
        TrackPoint closestPoint2 = null;

        for (int i = 0; i < trackA.size(); i++) {
            double distance = calculate3dDistance(trackA.get(i), trackB.get(i));
            averageDistance += distance;

            if (distance < minDistance) {
                minDistance = distance;
                closestPoint1 = trackA.get(i);
                closestPoint2 = trackB.get(i);
            }
        }
        
        // 计算平均距离
        averageDistance /= trackA.size();

        Result result = new Result(minDistance, averageDistance, closestPoint1, closestPoint2);

        return result;
    }

    // 航迹类
    static class TrackPoint {
        String time;
        double latitude;
        double longitude;
        double altitude;

        TrackPoint(String time, double latitude, double longitude, double altitude) {
            this.time = time;
            this.latitude = latitude;
            this.longitude = longitude;
            this.altitude = altitude;
        }
    }

    // 结果类
    static class Result {
        double minDistance;
        double averageDistance;
        TrackPoint closestPoint1;
        TrackPoint closestPoint2;

        Result(double minDistance, double averageDistance, TrackPoint closestPoint1, TrackPoint closestPoint2) {
            this.minDistance = minDistance;
            this.averageDistance = averageDistance;
            this.closestPoint1 = closestPoint1;
            this.closestPoint2 = closestPoint2;
        }
    }
}
