package org.example;

import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.apache.commons.math3.fitting.PolynomialCurveFitter;
import org.apache.commons.math3.fitting.WeightedObservedPoints;
import org.apache.commons.math3.stat.regression.SimpleRegression;

public class TrajectoryPredictionV1 {

    // 根据拟合方式返回多项式函数
    static PolynomialFunction fitTrajectory(double[] x, double[] y, int fittingType) {
        if (fittingType == 1) {
            // 线性拟合
            SimpleRegression regression = new SimpleRegression();
            for (int i = 0; i < x.length; i++) {
                regression.addData(x[i], y[i]);
            }
            // 将线性结果转化为多项式函数
            return new PolynomialFunction(new double[]{regression.getIntercept(), regression.getSlope()});
        } else if (fittingType == 2) {
            // 二次多项式拟合
            WeightedObservedPoints points = new WeightedObservedPoints();
            for (int i = 0; i < x.length; i++) {
                points.add(x[i], y[i]);
            }
            PolynomialCurveFitter fitter = PolynomialCurveFitter.create(2); // 二次拟合
            double[] coefficients = fitter.fit(points.toList());
            return new PolynomialFunction(coefficients);
        } else {
            throw new IllegalArgumentException("Unsupported fitting type: " + fittingType);
        }
    }
}
