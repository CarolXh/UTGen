package org.example;

import java.util.ArrayList;
import java.util.List;

public class UAVWaypointAdjustment {

    // 航迹类, 存储航迹点的时间、纬度、经度、高度
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

        @Override
        public String toString() {
            return "TrackPoint{" +
                    "time='" + time + '\'' +
                    ", latitude=" + latitude +
                    ", longitude=" + longitude +
                    ", altitude=" + altitude +
                    '}';
        }
    }

    public static List<TrackPoint>[] adjustUAVWaypoints(double altitudeThreshold, List<TrackPoint> uavAPoints, List<TrackPoint> uavBPoints) {
        List<TrackPoint> adjustedAPoints = new ArrayList<>();
        List<TrackPoint> adjustedBPoints = new ArrayList<>();

        for (int i = 0; i < uavAPoints.size(); i++) {
            TrackPoint pointA = uavAPoints.get(i);
            TrackPoint pointB = uavBPoints.get(i);

            double heightA = pointA.altitude;
            double heightB = pointB.altitude;

            // 策略是调整高度较高者，提高其高度至二者高度差满足阈值
            if (heightA > heightB && heightA - heightB < altitudeThreshold) {
                if (i < 25) {
                    // 前25秒逐渐提高高度
                    adjustedAPoints.add(new TrackPoint(pointA.time, pointA.latitude, pointA.longitude, heightA + (altitudeThreshold - (heightA - heightB)) * (i / 25.0)));
                } else if (i < 35) {
                    // 中间10秒维持调整后的高度
                    adjustedAPoints.add(new TrackPoint(pointA.time, pointA.latitude, pointA.longitude, heightB + altitudeThreshold));
                } else {
                    // 最后25秒逐渐回到原来的高度
                    adjustedAPoints.add(new TrackPoint(pointA.time, pointA.latitude, pointA.longitude, (heightB + altitudeThreshold) - (altitudeThreshold - (heightA - heightB)) * ((i - 35) / 25.0)));
                }
                adjustedBPoints.add(pointB);
            } else if (heightB > heightA && heightB - heightA < altitudeThreshold) {
                if (i < 25) {
                    // 前25秒逐渐提高高度
                    adjustedBPoints.add(new TrackPoint(pointB.time, pointB.latitude, pointB.longitude, heightB + (altitudeThreshold - (heightB - heightA)) * (i / 25.0)));
                } else if (i < 35) {
                    // 中间10秒维持调整后的高度
                    adjustedBPoints.add(new TrackPoint(pointB.time, pointB.latitude, pointB.longitude, heightA + altitudeThreshold));
                } else {
                    // 最后25秒逐渐回到原来的高度
                    adjustedBPoints.add(new TrackPoint(pointB.time, pointB.latitude, pointB.longitude, (heightA + altitudeThreshold) - (altitudeThreshold - (heightB - heightA)) * ((i - 35) / 25.0)));
                }
                adjustedAPoints.add(pointA);
            } else {
                adjustedAPoints.add(pointA);
                adjustedBPoints.add(pointB);
            }
        }

        return new List[]{adjustedAPoints, adjustedBPoints};
    }

}