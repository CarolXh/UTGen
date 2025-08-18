package org.example;

import java.util.List;

public class interpolation {
    public void alignTrajectoryBToA(List<TrackPoint4Alg> trajectoryA, List<TrackPoint4Alg> trajectoryB) {
        for (TrackPoint4Alg pointA : trajectoryA) {
            // 找到 B 航迹中时间在 pointA 之前和之后的两个最接近的点
            TrackPoint4Alg closestPointB1 = findClosestPointBefore(pointA, trajectoryB);
            TrackPoint4Alg closestPointB2 = findClosestPointAfter(pointA, trajectoryB);

            // 如果找到了时间接近的两个点
            if (closestPointB1 != null && closestPointB2 != null) {
                // 使用这两个点对 B 航迹进行插值
                TrackPoint4Alg interpolatedPointB = linearInterpolate(closestPointB1, closestPointB2, pointA.getTimestamp());

                // 计算 A 和 B 航迹点之间的空间距离
                double distance = calculateDistance(pointA, interpolatedPointB);
                System.out.println("Distance between A and interpolated B: " + distance);
            }
        }
    }

    // 找到 B 航迹中时间小于 pointA 时间的最接近的点
    public TrackPoint4Alg findClosestPointBefore(TrackPoint4Alg pointA, List<TrackPoint4Alg> trajectoryB) {
        TrackPoint4Alg closestPoint = null;
        long maxTimeDiff = Long.MAX_VALUE;

        for (TrackPoint4Alg pointB : trajectoryB) {
            if (pointB.getTimestamp() < pointA.getTimestamp()) {
                long timeDiff = pointA.getTimestamp() - pointB.getTimestamp();
                if (timeDiff < maxTimeDiff) {
                    closestPoint = pointB;
                    maxTimeDiff = timeDiff;
                }
            }
        }

        return closestPoint;
    }

    // 找到 B 航迹中时间大于 pointA 时间的最接近的点
    public TrackPoint4Alg findClosestPointAfter(TrackPoint4Alg pointA, List<TrackPoint4Alg> trajectoryB) {
        TrackPoint4Alg closestPoint = null;
        long minTimeDiff = Long.MAX_VALUE;

        for (TrackPoint4Alg pointB : trajectoryB) {
            if (pointB.getTimestamp() > pointA.getTimestamp()) {
                long timeDiff = pointB.getTimestamp() - pointA.getTimestamp();
                if (timeDiff < minTimeDiff) {
                    closestPoint = pointB;
                    minTimeDiff = timeDiff;
                }
            }
        }

        return closestPoint;
    }

    // 线性插值，获取在指定时间上的坐标
    public TrackPoint4Alg linearInterpolate(TrackPoint4Alg p1, TrackPoint4Alg p2, long targetTime) {
        double x1 = p1.getLongitude(), y1 = p1.getLatitude(), z1 = p1.getAltitude();
        double x2 = p2.getLongitude(), y2 = p2.getLatitude(), z2 = p2.getAltitude();

        long t1 = p1.getTimestamp(), t2 = p2.getTimestamp();

        // 线性插值公式
        double interpolatedX = x1 + (targetTime - t1) * (x2 - x1) / (t2 - t1);
        double interpolatedY = y1 + (targetTime - t1) * (y2 - y1) / (t2 - t1);
        double interpolatedZ = z1 + (targetTime - t1) * (z2 - z1) / (t2 - t1);

        return new TrackPoint4Alg(p1.getName(), targetTime, interpolatedX, interpolatedY, interpolatedZ, 
                                0, 0, 0, 0, 0, 0);
    }

    // 计算两个点之间的空间距离
    public double calculateDistance(TrackPoint4Alg p1, TrackPoint4Alg p2) {
        double dx = p1.getLongitude() - p2.getLongitude();
        double dy = p1.getLatitude() - p2.getLatitude();
        double dz = p1.getAltitude() - p2.getAltitude();
        return Math.sqrt(dx * dx + dy * dy + dz * dz);
    }

}
