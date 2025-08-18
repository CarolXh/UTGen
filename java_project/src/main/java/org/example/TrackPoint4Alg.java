package org.example;

public class TrackPoint4Alg {
    // 设备名称
    private String name;
    // 时间戳
    private long timestamp;
    // 经度
    private double longitude;
    // 纬度
    private double latitude;
    // 高度
    private double altitude;
    // 北向速度
    private double northVelocity;
    // 东向速度
    private double eastVelocity;
    // 地向速度
    private double downVelocity;
    // 北向加速度
    private double northAcceleration;
    // 东向加速度
    private double eastAcceleration;
    // 地向加速度
    private double downAcceleration;

    // 构造方法
    public TrackPoint4Alg(String name, long timestamp, double longitude, double latitude, double altitude,
                          double northVelocity, double eastVelocity, double downVelocity,
                          double northAcceleration, double eastAcceleration, double downAcceleration) {
        this.name = name;
        this.timestamp = timestamp;
        this.longitude = longitude;
        this.latitude = latitude;
        this.altitude = altitude;
        this.northVelocity = northVelocity;
        this.eastVelocity = eastVelocity;
        this.downVelocity = downVelocity;
        this.northAcceleration = northAcceleration;
        this.eastAcceleration = eastAcceleration;
        this.downAcceleration = downAcceleration;
    }

    // Getter 和 Setter 方法
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(long timestamp) {
        this.timestamp = timestamp;
    }

    public double getLongitude() {
        return longitude;
    }

    public void setLongitude(double longitude) {
        this.longitude = longitude;
    }

    public double getLatitude() {
        return latitude;
    }

    public void setLatitude(double latitude) {
        this.latitude = latitude;
    }

    public double getAltitude() {
        return altitude;
    }

    public void setAltitude(double altitude) {
        this.altitude = altitude;
    }

    public double getNorthVelocity() {
        return northVelocity;
    }

    public void setNorthVelocity(double northVelocity) {
        this.northVelocity = northVelocity;
    }

    public double getEastVelocity() {
        return eastVelocity;
    }

    public void setEastVelocity(double eastVelocity) {
        this.eastVelocity = eastVelocity;
    }

    public double getDownVelocity() {
        return downVelocity;
    }

    public void setDownVelocity(double downVelocity) {
        this.downVelocity = downVelocity;
    }

    public double getNorthAcceleration() {
        return northAcceleration;
    }

    public void setNorthAcceleration(double northAcceleration) {
        this.northAcceleration = northAcceleration;
    }

    public double getEastAcceleration() {
        return eastAcceleration;
    }

    public void setEastAcceleration(double eastAcceleration) {
        this.eastAcceleration = eastAcceleration;
    }

    public double getDownAcceleration() {
        return downAcceleration;
    }

    public void setDownAcceleration(double downAcceleration) {
        this.downAcceleration = downAcceleration;
    }

    // 重写 toString 方法，方便打印对象信息
    @Override
    public String toString() {
        return "TrackPoint4Alg{" +
                "name='" + name + '\'' +
                ", timestamp=" + timestamp +
                ", longitude=" + longitude +
                ", latitude=" + latitude +
                ", altitude=" + altitude +
                ", northVelocity=" + northVelocity +
                ", eastVelocity=" + eastVelocity +
                ", downVelocity=" + downVelocity +
                ", northAcceleration=" + northAcceleration +
                ", eastAcceleration=" + eastAcceleration +
                ", downAcceleration=" + downAcceleration +
                '}';
    }

}