package org.example;

import javax.swing.*;
import java.awt.*;
import java.awt.geom.Ellipse2D;
import java.awt.image.BufferedImage;
import java.io.*;
import java.util.ArrayList;
import java.util.List;
import javax.imageio.ImageIO;
import java.util.Random;
import java.util.stream.Collectors;

public class TrajectoryVisualization {

    static final List<double[]> truePositions = new ArrayList<>();
    static final List<double[]> measurements = new ArrayList<>();
    static final List<double[]> futurePredictions = new ArrayList<>();


    // 从 CSV 文件读取数据
    static boolean readCsvData(String filePath) {
        // 首先尝试从resources加载
        InputStream inputStream = TrajectoryVisualization.class.getClassLoader().getResourceAsStream(filePath);
        if (inputStream == null) {
            // 如果资源不存在，尝试从文件系统加载
            try {
                File file = new File(filePath);
                if (!file.exists()) {
                    System.err.println("CSV文件不存在，将生成示例数据");
                    generateSampleData();
                    return true;
                }
                inputStream = new FileInputStream(file);
            } catch (FileNotFoundException e) {
                System.err.println("无法打开CSV文件: " + e.getMessage());
                generateSampleData();
                return true;
            }
        }

        try (BufferedReader br = new BufferedReader(new InputStreamReader(inputStream))) {
            // 跳过表头
            br.readLine();
            String line;

            while ((line = br.readLine()) != null) {
                String[] values = line.split(",");
                double time = Double.parseDouble(values[0]);
                double lon = Double.parseDouble(values[1]);
                double lat = Double.parseDouble(values[2]);
                double alt = Double.parseDouble(values[3]);

                truePositions.add(new double[]{time, lon, lat, alt});

                // 添加模拟测量数据（带噪声）
                Random random = new Random();
                double noiseLon = lon + random.nextGaussian() * 0.00001;
                double noiseLat = lat + random.nextGaussian() * 0.00001;
                double noiseAlt = alt + random.nextGaussian() * 0.01;
                measurements.add(new double[]{time, noiseLon, noiseLat, noiseAlt});
            }

            return true;
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }

    // 生成示例数据
    static void generateSampleData() {
        Random random = new Random();
        for (int i = 0; i < 100; i++) {
            double time = i * 0.1;
            double lon = 120.0 + i * 0.001;
            double lat = 30.0 + i * 0.001;
            double alt = 100.0 + i * 0.5;

            truePositions.add(new double[]{time, lon, lat, alt});
            measurements.add(new double[]{
                time,
                lon + random.nextGaussian() * 0.0001,
                lat + random.nextGaussian() * 0.0001,
                alt + random.nextGaussian() * 0.1
            });
        }
    }

    // 保存静态图像
    static void saveFrames(TrajectoryPanel panel, int width, int height, String filePrefix) {
        for (int frame = 0; frame < measurements.size(); frame++) {
            panel.setFrame(frame);

            // 创建 BufferedImage 并绘制内容
            BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
            Graphics2D g2d = image.createGraphics();
            panel.paintComponent(g2d);
            g2d.dispose();

            // 保存为 PNG 文件
            File outputFile = new File(filePrefix + "_" + frame + ".png");
            try {
                ImageIO.write(image, "png", outputFile);
                System.out.println("Saved: " + outputFile.getAbsolutePath());
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    // 绘图面板
    static class TrajectoryPanel extends JPanel {
        private final int width, height;
        private int currentFrame = 0;

        public TrajectoryPanel(int width, int height) {
            this.width = width;
            this.height = height;
        }

        public void setFrame(int frame) {
            this.currentFrame = frame;

            // 更新未来预测数据
            if (frame < measurements.size()) {
                double[] currentState = measurements.get(frame);
                futurePredictions.clear();

                for (int i = 1; i <= 10; i++) { // 未来 10 秒，每秒一个点
                    double futureLon = currentState[1] + i * 0.0001; // 简单线性预测
                    double futureLat = currentState[2] + i * 0.0001;
                    double futureAlt = currentState[3];
                    futurePredictions.add(new double[]{futureLon, futureLat, futureAlt});
                }
            }

            repaint();
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            Graphics2D g2d = (Graphics2D) g;

            // 背景
            g2d.setColor(Color.WHITE);
            g2d.fillRect(0, 0, width, height);

            // 坐标系范围
            double lonMin = 119.0, lonMax = 121.0, latMin = 29.0, latMax = 31.0;

            // 绘制网格
            g2d.setColor(Color.LIGHT_GRAY);
            for (int i = 0; i <= 10; i++) {
                int x = i * width / 10;
                int y = i * height / 10;
                g2d.drawLine(x, 0, x, height); // 垂直线
                g2d.drawLine(0, y, width, y); // 水平线
            }

            // 绘制真实轨迹
            g2d.setColor(Color.GREEN);
            for (int i = 0; i < currentFrame; i++) {
                double[] pos = truePositions.get(i);
                drawPoint(g2d, pos, lonMin, lonMax, latMin, latMax, Color.GREEN);
            }

            // 绘制测量数据
            g2d.setColor(Color.RED);
            for (int i = 0; i < currentFrame; i++) {
                double[] meas = measurements.get(i);
                drawPoint(g2d, meas, lonMin, lonMax, latMin, latMax, Color.RED);
            }

            // 绘制未来预测
            g2d.setColor(Color.BLUE);
            for (double[] future : futurePredictions) {
                drawPoint(g2d, future, lonMin, lonMax, latMin, latMax, Color.BLUE);
            }

            // 绘制坐标轴标签
            g2d.setColor(Color.BLACK);
            g2d.drawString("Longitude", width / 2 - 20, height - 10);
            g2d.drawString("Latitude", 10, height / 2);
        }

        // 绘制点
        void drawPoint(Graphics2D g2d, double[] pos, double lonMin, double lonMax, double latMin, double latMax, Color color) {
            int x = (int) ((pos[1] - lonMin) / (lonMax - lonMin) * width);
            int y = (int) ((latMax - pos[2]) / (latMax - latMin) * height);
            g2d.setColor(color);
            g2d.fill(new Ellipse2D.Double(x - 2, y - 2, 4, 4));
        }
    }
}
