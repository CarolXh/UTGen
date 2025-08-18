package org.example;

import java.util.ArrayList;
import java.util.List;

class TrackPredMotionEquation {

    // 地球半径 (单位: 米)
    static final double EARTH_RADIUS = 6371000.0;
    // 最大速度 (单位: 米/秒)
    static final double MAX_VELOCITY = 40.0;

    /**
     * 预测无人机的未来轨迹。
     *
     * @param currentState 无人机的当前状态
     * @param predictionTime 预测时间 (单位: 秒)
     * @param timeStep 时间步长 (单位: 秒)
     * @return 预测轨迹的列表
     */
    public List<double[]> predictTrajectory(double[] currentState, double predictionTime, double timeStep) {
        // 提取当前状态
        double timestamp = currentState[0];
        double longitude = currentState[1];
        double latitude = currentState[2];
        double altitude = currentState[3];
        double vNorth = currentState[4];
        double vEast = currentState[5];
        double vDown = currentState[6];
        double aNorth = currentState[7];
        double aEast = currentState[8];
        double aDown = currentState[9];

        // 保存预测轨迹
        List<double[]> trajectory = new ArrayList<>();

        // 预测未来轨迹
        for (double t = 0; t <= predictionTime; t += timeStep) {
            // 更新位置
            double deltaNorth = vNorth * timeStep + 0.5 * aNorth * timeStep * timeStep;
            double deltaEast = vEast * timeStep + 0.5 * aEast * timeStep * timeStep;
            double deltaDown = vDown * timeStep + 0.5 * aDown * timeStep * timeStep;

            // 更新速度
            vNorth += aNorth * timeStep;
            vEast += aEast * timeStep;
            vDown += aDown * timeStep;

            // 限制平飞速度
            double resultantVelocity = Math.sqrt(vNorth * vNorth + vEast * vEast);
            if (resultantVelocity > MAX_VELOCITY) {
                vNorth = vNorth * MAX_VELOCITY / resultantVelocity;
                vEast = vEast * MAX_VELOCITY / resultantVelocity;
            }

            // 将北向和东向位移转换为经度和纬度变化
            latitude += Math.toDegrees(deltaNorth / EARTH_RADIUS);
            longitude += Math.toDegrees(deltaEast / (EARTH_RADIUS * Math.cos(Math.toRadians(latitude))));
            altitude += deltaDown;

            // 保存轨迹点
            trajectory.add(new double[]{timestamp + t, longitude, latitude, altitude});
        }

        return trajectory;
    }

    /**
     * 打印预测轨迹。
     *
     * @param trajectory 预测的轨迹
     */
    public void printTrajectory(List<double[]> trajectory) {
        System.out.println("Time(s)\tLongitude\tLatitude\tAltitude(m)");
        for (double[] point : trajectory) {
            System.out.printf("%.1f\t%.6f\t%.6f\t%.2f\n", point[0], point[1], point[2], point[3]);
        }
    }

}
