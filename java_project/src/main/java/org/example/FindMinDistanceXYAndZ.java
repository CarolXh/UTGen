package org.example;

import java.util.ArrayList;
import java.util.List;

class TrackPoint {
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

public class FindMinDistanceXYAndZ {

    public static double haversineDistance(double lat1, double lon1, double lat2, double lon2) {
        final double R = 6371000; // Radius of Earth in meters
        double phi1 = Math.toRadians(lat1);
        double phi2 = Math.toRadians(lat2);
        double deltaPhi = Math.toRadians(lat2 - lat1);
        double deltaLambda = Math.toRadians(lon2 - lon1);

        double a = Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
                   Math.cos(phi1) * Math.cos(phi2) *
                   Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return R * c;
    }

    public static Result findMinDistances(List<TrackPoint> uavA, List<TrackPoint> uavB) {
        double minHorizontalDistance = Double.MAX_VALUE;
        double minVerticalDistance = Double.MAX_VALUE;

        List<Pair> minHorizontalPoints = new ArrayList<>();
        List<Pair> minVerticalPoints = new ArrayList<>();

        for (int i = 0; i < uavA.size(); i++) {
            TrackPoint pointA = uavA.get(i);
            TrackPoint pointB = uavB.get(i);

            double horizontalDistance = haversineDistance(pointA.latitude, pointA.longitude, pointB.latitude, pointB.longitude);
            double verticalDistance = Math.abs(pointA.altitude - pointB.altitude);

            if (horizontalDistance < minHorizontalDistance) {
                minHorizontalDistance = horizontalDistance;
                minHorizontalPoints.clear();
                minHorizontalPoints.add(new Pair(pointA, pointB));
            } else if (horizontalDistance == minHorizontalDistance) {
                minHorizontalPoints.add(new Pair(pointA, pointB));
            }

            if (verticalDistance < minVerticalDistance) {
                minVerticalDistance = verticalDistance;
                minVerticalPoints.clear();
                minVerticalPoints.add(new Pair(pointA, pointB));
            } else if (verticalDistance == minVerticalDistance) {
                minVerticalPoints.add(new Pair(pointA, pointB));
            }
        }

        return new Result(minHorizontalPoints, minHorizontalDistance, minVerticalPoints, minVerticalDistance);
    }

    public static class Pair {
        TrackPoint pointA;
        TrackPoint pointB;

        Pair(TrackPoint pointA, TrackPoint pointB) {
            this.pointA = pointA;
            this.pointB = pointB;
        }

        @Override
        public String toString() {
            return "Pair{" +
                    "pointA=" + pointA +
                    ", pointB=" + pointB +
                    '}';
        }
    }

    public static class Result {
        List<Pair> horizontalPairs;
        double minHorizontalDistance;
        List<Pair> verticalPairs;
        double minVerticalDistance;

        Result(List<Pair> horizontalPairs, double minHorizontalDistance, List<Pair> verticalPairs, double minVerticalDistance) {
            this.horizontalPairs = horizontalPairs;
            this.minHorizontalDistance = minHorizontalDistance;
            this.verticalPairs = verticalPairs;
            this.minVerticalDistance = minVerticalDistance;
        }

        @Override
        public String toString() {
            return "Result{" +
                    "horizontalPairs=" + horizontalPairs +
                    ", minHorizontalDistance=" + minHorizontalDistance +
                    ", verticalPairs=" + verticalPairs +
                    ", minVerticalDistance=" + minVerticalDistance +
                    '}';
        }
    }

}
