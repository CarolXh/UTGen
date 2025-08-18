package org.example;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;



public class TrajectoryPrediction {


    public static List<Record> predictTrajectory(List<Record> historyData, int futurePeriod) throws ParseException {

        // 清洗数据并解析
        List<Double> relativeTimes = new ArrayList<>();
        List<Double> latitudes = new ArrayList<>();
        List<Double> longitudes = new ArrayList<>();
        List<Double> altitudes = new ArrayList<>();

        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        Date baseTime = sdf.parse(historyData.get(historyData.size() - 1).time);

        for (Record record : historyData) {
            Date recordTime = sdf.parse(record.time);
            relativeTimes.add((recordTime.getTime() - baseTime.getTime()) / 1000.0); // 转为秒
            latitudes.add(record.latitude);
            longitudes.add(record.longitude);
            altitudes.add(record.altitude);
        }

        // 拟合纬度、经度和高度
        double[] latCoef = fitPolynomial(relativeTimes, latitudes, 2);
        double[] lonCoef = fitPolynomial(relativeTimes, longitudes, 2);
        double[] altCoef = fitPolynomial(relativeTimes, altitudes, 2);

        List<Record> futureTra = new ArrayList<>();

        // 预测未来 60 秒轨迹
        for (int t = 1; t <= 60; t++) {
            double futureLatitude = evaluatePolynomial(latCoef, t);
            double futureLongitude = evaluatePolynomial(lonCoef, t);
            double futureAltitude = evaluatePolynomial(altCoef, t);
            Date futureTime = new Date(baseTime.getTime() + t * 1000L);

            Record temp = new Record(futureTime, futureLatitude, futureLongitude, futureAltitude);
            futureTra.add(temp);
        }

        return futureTra;
    }

    // 最小二乘法拟合
    public static double[] fitPolynomial(List<Double> x, List<Double> y, int degree) {
        int n = x.size();
        int m = degree + 1;

        // 构造 X 矩阵
        double[][] X = new double[n][m];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                X[i][j] = Math.pow(x.get(i), m - j - 1);
            }
        }

        // 构造 XT 矩阵
        double[][] XT = transposeMatrix(X);

        // 计算 XT * X
        double[][] XT_X = multiplyMatrices(XT, X);

        // 计算 XT * y
        double[] XT_y = new double[m];
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                XT_y[i] += XT[i][j] * y.get(j);
            }
        }

        // 使用高斯消去法解线性方程组
        return solveLinearSystem(XT_X, XT_y);
    }

    // 高斯消去法解线性方程组
    public static double[] solveLinearSystem(double[][] A, double[] b) {
        int n = A.length;

        for (int i = 0; i < n; i++) {
            // 寻找主元
            int maxRow = i;
            for (int k = i + 1; k < n; k++) {
                if (Math.abs(A[k][i]) > Math.abs(A[maxRow][i])) {
                    maxRow = k;
                }
            }

            // 交换行
            double[] tempRow = A[i];
            A[i] = A[maxRow];
            A[maxRow] = tempRow;

            double tempValue = b[i];
            b[i] = b[maxRow];
            b[maxRow] = tempValue;

            // 消元
            for (int k = i + 1; k < n; k++) {
                double factor = A[k][i] / A[i][i];
                for (int j = i; j < n; j++) {
                    A[k][j] -= factor * A[i][j];
                }
                b[k] -= factor * b[i];
            }
        }

        // 回代求解
        double[] x = new double[n];
        for (int i = n - 1; i >= 0; i--) {
            x[i] = b[i] / A[i][i];
            for (int k = i - 1; k >= 0; k--) {
                b[k] -= A[k][i] * x[i];
            }
        }
        return x;
    }

    // 计算多项式值
    public static double evaluatePolynomial(double[] coef, double x) {
        double result = 0;
        for (int i = 0; i < coef.length; i++) {
            result = result * x + coef[i];
        }
        return result;
    }

    // 矩阵转置
    public static double[][] transposeMatrix(double[][] matrix) {
        int rows = matrix.length;
        int cols = matrix[0].length;
        double[][] transposed = new double[cols][rows];

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                transposed[j][i] = matrix[i][j];
            }
        }
        return transposed;
    }

    // 矩阵相乘
    public static double[][] multiplyMatrices(double[][] A, double[][] B) {
        int rowsA = A.length;
        int colsA = A[0].length;
        int colsB = B[0].length;
        double[][] result = new double[rowsA][colsB];

        for (int i = 0; i < rowsA; i++) {
            for (int j = 0; j < colsB; j++) {
                for (int k = 0; k < colsA; k++) {
                    result[i][j] += A[i][k] * B[k][j];
                }
            }
        }
        return result;
    }

    // 数据记录类
    static class Record {
        String time;
        double latitude;
        double longitude;
        double altitude;

        double vx;
        double vy;
        double vz;

        Record(String time, double latitude, double longitude, double altitude, double vx, double vy, double vz) {
            this.time = time;
            this.latitude = latitude;
            this.longitude = longitude;
            this.altitude = altitude;
            this.vx = vx;
            this.vy = vy;
            this.vz = vz;
        }

        public Record(Date futureTime, double futureLatitude, double futureLongitude, double futureAltitude) {
        }
    }
}
