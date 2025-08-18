
package org.example;

import static org.junit.Assert.*;
import java.util.ArrayList;
import java.util.List;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

public class DataCleanerTest {
    private DataCleaner dataCleaner;
    private TrackPoint4Alg mockTrackPoint;

    @Before
    public void setUp() {
        dataCleaner = new DataCleaner();
        mockTrackPoint = Mockito.mock(TrackPoint4Alg.class);
    }

    @Test
    public void testCleanData_WithEmptyInput() {
        List<TrackPoint4Alg> input = new ArrayList<>();
        List<TrackPoint4Alg> result = DataCleaner.cleanData(input);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testCleanData_WithOneValidPoint() {
        Mockito.when(mockTrackPoint.getLatitude()).thenReturn(10.0);
        Mockito.when(mockTrackPoint.getLongitude()).thenReturn(20.0);
        Mockito.when(mockTrackPoint.getAltitude()).thenReturn(30.0);
        List<TrackPoint4Alg> input = new ArrayList<>();
        input.add(mockTrackPoint);
        List<TrackPoint4Alg> result = DataCleaner.cleanData(input);
        assertTrue(result.contains(mockTrackPoint));
    }

    @Test
    public void testCleanData_WithOneInvalidPoint_DueToLatitudeNaN() {
        Mockito.when(mockTrackPoint.getLatitude()).thenReturn(Double.NaN);
        Mockito.when(mockTrackPoint.getLongitude()).thenReturn(20.0);
        Mockito.when(mockTrackPoint.getAltitude()).thenReturn(30.0);
        List<TrackPoint4Alg> input = new ArrayList<>();
        input.add(mockTrackPoint);
        List<TrackPoint4Alg> result = DataCleaner.cleanData(input);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testCleanData_WithOneInvalidPoint_DueToLongitudeNaN() {
        Mockito.when(mockTrackPoint.getLatitude()).thenReturn(10.0);
        Mockito.when(mockTrackPoint.getLongitude()).thenReturn(Double.NaN);
        Mockito.when(mockTrackPoint.getAltitude()).thenReturn(30.0);
        List<TrackPoint4Alg> input = new ArrayList<>();
        input.add(mockTrackPoint);
        List<TrackPoint4Alg> result = DataCleaner.cleanData(input);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testCleanData_WithOneInvalidPoint_DueToAltitudeNaN() {
        Mockito.when(mockTrackPoint.getLatitude()).thenReturn(10.0);
        Mockito.when(mockTrackPoint.getLongitude()).thenReturn(20.0);
        Mockito.when(mockTrackPoint.getAltitude()).thenReturn(Double.NaN);
        List<TrackPoint4Alg> input = new ArrayList<>();
        input.add(mockTrackPoint);
        List<TrackPoint4Alg> result = DataCleaner.cleanData(input);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testCleanData_WithOneInvalidPoint_DueToLatitudeOutOfRange() {
        Mockito.when(mockTrackPoint.getLatitude()).thenReturn(100.0);
        Mockito.when(mockTrackPoint.getLongitude()).thenReturn(20.0);
        Mockito.when(mockTrackPoint.getAltitude()).thenReturn(30.0);
        List<TrackPoint4Alg> input = new ArrayList<>();
        input.add(mockTrackPoint);
        List<TrackPoint4Alg> result = DataCleaner.cleanData(input);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testCleanData_WithOneInvalidPoint_DueToLongitudeOutOfRange() {
        Mockito.when(mockTrackPoint.getLatitude()).thenReturn(10.0);
        Mockito.when(mockTrackPoint.getLongitude()).thenReturn(200.0);
        Mockito.when(mockTrackPoint.getAltitude()).thenReturn(30.0);
        List<TrackPoint4Alg> input = new ArrayList<>();
        input.add(mockTrackPoint);
        List<TrackPoint4Alg> result = DataCleaner.cleanData(input);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testCleanData_WithOneInvalidPoint_DueToAltitudeOutOfRange() {
        Mockito.when(mockTrackPoint.getLatitude()).thenReturn(10.0);
        Mockito.when(mockTrackPoint.getLongitude()).thenReturn(20.0);
        Mockito.when(mockTrackPoint.getAltitude()).thenReturn(-1.0);
        List<TrackPoint4Alg> input = new ArrayList<>();
        input.add(mockTrackPoint);
        List<TrackPoint4Alg> result = DataCleaner.cleanData(input);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testCleanData_WithTwoPoints_SecondInvalid_DueToInconsistency() {
        TrackPoint4Alg mockTrackPointFirst = Mockito.mock(TrackPoint4Alg.class);
        Mockito.when(mockTrackPointFirst.getLatitude()).thenReturn(10.0);
        Mockito.when(mockTrackPointFirst.getLongitude()).thenReturn(20.0);
        Mockito.when(mockTrackPointFirst.getAltitude()).thenReturn(30.0);

        TrackPoint4Alg mockTrackPointSecond = Mockito.mock(TrackPoint4Alg.class);
        Mockito.when(mockTrackPointSecond.getLatitude()).thenReturn(100.0);
        Mockito.when(mockTrackPointSecond.getLongitude()).thenReturn(120.0);
        Mockito.when(mockTrackPointSecond.getAltitude()).thenReturn(30.0);

        List<TrackPoint4Alg> input = new ArrayList<>();
        input.add(mockTrackPointFirst);
        input.add(mockTrackPointSecond);

        List<TrackPoint4Alg> result = DataCleaner.cleanData(input);
        assertTrue(result.contains(mockTrackPointFirst));
        assertFalse(result.contains(mockTrackPointSecond));
    }

    @Test
    public void testCleanData_WithMultipleValidPoints() {
        TrackPoint4Alg mockTrackPointFirst = Mockito.mock(TrackPoint4Alg.class);
        Mockito.when(mockTrackPointFirst.getLatitude()).thenReturn(10.0);
        Mockito.when(mockTrackPointFirst.getLongitude()).thenReturn(20.0);
        Mockito.when(mockTrackPointFirst.getAltitude()).thenReturn(30.0);

        TrackPoint4Alg mockTrackPointSecond = Mockito.mock(TrackPoint4Alg.class);
        Mockito.when(mockTrackPointSecond.getLatitude()).thenReturn(10.001); // 确保距离小于1000米
        Mockito.when(mockTrackPointSecond.getLongitude()).thenReturn(20.001);
        Mockito.when(mockTrackPointSecond.getAltitude()).thenReturn(30.0);

        List<TrackPoint4Alg> input = new ArrayList<>();
        input.add(mockTrackPointFirst);
        input.add(mockTrackPointSecond);

        List<TrackPoint4Alg> result = DataCleaner.cleanData(input);
        assertTrue(result.contains(mockTrackPointFirst));
        assertTrue(result.contains(mockTrackPointSecond));
    }
}
