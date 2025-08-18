package org.example;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class FlightPathConsistencyCheck {


    public class UAVPositionCheck {

        // 地球半径（米）
        private static final double EARTH_RADIUS = 6371000.0;
    
        /**
         * 计算两点之间的 Haversine 距离
         */
        public static double haversine(double lat1, double lon1, double lat2, double lon2) {
            // 将经纬度从度转换为弧度
            double lat1Rad = Math.toRadians(lat1);
            double lon1Rad = Math.toRadians(lon1);
            double lat2Rad = Math.toRadians(lat2);
            double lon2Rad = Math.toRadians(lon2);
    
            // 计算差值
            double dLat = lat2Rad - lat1Rad;
            double dLon = lon2Rad - lon1Rad;
    
            // Haversine 公式
            double a = Math.pow(Math.sin(dLat / 2), 2) +
                       Math.cos(lat1Rad) * Math.cos(lat2Rad) * Math.pow(Math.sin(dLon / 2), 2);
            double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    
            // 计算距离
            return EARTH_RADIUS * c;
        }
    
        /**
         * 将地理坐标转换为笛卡尔坐标
         */
        public static double[] geodeticToCartesian(double lat, double lon, double h) {
            // 将经纬度从度转换为弧度
            double latRad = Math.toRadians(lat);
            double lonRad = Math.toRadians(lon);
    
            // 计算笛卡尔坐标
            double x = (EARTH_RADIUS + h) * Math.cos(latRad) * Math.cos(lonRad);
            double y = (EARTH_RADIUS + h) * Math.cos(latRad) * Math.sin(lonRad);
            double z = (EARTH_RADIUS + h) * Math.sin(latRad);
    
            return new double[]{x, y, z};
        }
    
        /**
         * 将笛卡尔坐标转换回地理坐标
         */
        public static double[] cartesianToGeodetic(double x, double y, double z) {
            // 计算经纬度和高度
            double lon = Math.toDegrees(Math.atan2(y, x));
            double lat = Math.toDegrees(Math.asin(z / Math.sqrt(x * x + y * y + z * z)));
            double h = Math.sqrt(x * x + y * y + z * z) - EARTH_RADIUS;
    
            return new double[]{lat, lon, h};
        }
    
        /**
         * 计算垂足位置
         */
        public static double[] calculateFootPoint(double latP, double lonP, double hP,
                                                  double latA, double lonA, double hA,
                                                  double latB, double lonB, double hB) {
            // 将地理坐标转换为笛卡尔坐标
            double[] P = geodeticToCartesian(latP, lonP, hP);
            double[] A = geodeticToCartesian(latA, lonA, hA);
            double[] B = geodeticToCartesian(latB, lonB, hB);
    
            // 计算航线方向向量
            double[] d = {B[0] - A[0], B[1] - A[1], B[2] - A[2]};
    
            // 计算垂足参数 t
            double t = ((P[0] - A[0]) * d[0] + (P[1] - A[1]) * d[1] + (P[2] - A[2]) * d[2]) /
                       (d[0] * d[0] + d[1] * d[1] + d[2] * d[2]);
    
            // 计算垂足坐标
            double[] F = {
                A[0] + t * d[0],
                A[1] + t * d[1],
                A[2] + t * d[2]
            };
    
            // 将垂足从笛卡尔坐标转换回地理坐标
            return cartesianToGeodetic(F[0], F[1], F[2]);
        }
    }



    // Haversine formula: Calculate the horizontal distance between two points (in meters)
    public static double haversine(double lon1, double lat1, double lon2, double lat2) {
        final double R = 6371000; // Earth's radius in meters

        // Convert degrees to radians
        lon1 = Math.toRadians(lon1);
        lat1 = Math.toRadians(lat1);
        lon2 = Math.toRadians(lon2);
        lat2 = Math.toRadians(lat2);

        // Haversine formula
        double dlon = lon2 - lon1;
        double dlat = lat2 - lat1;
        double a = Math.sin(dlat / 2) * Math.sin(dlat / 2)
                + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) * Math.sin(dlon / 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return R * c;
    }

    // Calculate vertical distance (altitude difference)
    public static double verticalDistance(double alt1, double alt2) {
        return Math.abs(alt1 - alt2);
    }

    // Check if the UAV's current position meets the threshold conditions
    public static boolean checkThreshold(double[] currentPos, List<double[]> waypoints, double horizontalThreshold, double verticalThreshold) {
        double lon1 = currentPos[0];
        double lat1 = currentPos[1];
        double alt1 = currentPos[2];

        for (double[] waypoint : waypoints) {
            double lon2 = waypoint[0];
            double lat2 = waypoint[1];
            double alt2 = waypoint[2];

            // Calculate horizontal distance
            double horizontalDist = haversine(lon1, lat1, lon2, lat2);

            // Calculate vertical distance
            double verticalDist = verticalDistance(alt1, alt2);

            // Check if any threshold is met
            if (horizontalDist <= horizontalThreshold || verticalDist <= verticalThreshold) {
                return true;
            }
        }

        return false;
    }

    // Read CSV file and parse waypoints
    public static List<double[]> readCSV(String filePath) throws IOException {
        List<double[]> waypoints = new ArrayList<>();

        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            boolean isFirstLine = true; // Skip header

            while ((line = br.readLine()) != null) {
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }

                String[] parts = line.split(",");
                double lat = Double.parseDouble(parts[1]);
                double lon = Double.parseDouble(parts[2]);
                double alt = Double.parseDouble(parts[3]);

                waypoints.add(new double[]{lon, lat, alt});
            }
        }

        return waypoints;
    }


}
