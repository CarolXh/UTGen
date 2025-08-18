
package org.example;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

@ExtendWith(MockitoExtension.class)
public class DataCleanerTest {
    
    @Mock
    private TrackPoint4Alg mockTrackPoint1;
    @Mock
    private TrackPoint4Alg mockTrackPoint2;
    @Mock
    private TrackPoint4Alg mockTrackPoint3;
    @Mock
    private TrackPoint4Alg mockTrackPoint4;

    private DataCleaner dataCleaner;

    @BeforeEach
    public void setUp() {
        dataCleaner = new DataCleaner();
    }

    @Test
    public void testCleanDataWithNoPoints() {
        List<TrackPoint4Alg> input = new ArrayList<>();
        List<TrackPoint4Alg> result = dataCleaner.cleanData(input);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testCleanDataWithValidPoints() throws Exception {
        List<TrackPoint4Alg> input = new ArrayList<>();
        when(mockTrackPoint1.getLatitude()).thenReturn(45.0);
        when(mockTrackPoint1.getLongitude()).thenReturn(-45.0);
        when(mockTrackPoint1.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint1);

        when(mockTrackPoint2.getLatitude()).thenReturn(46.0);
        when(mockTrackPoint2.getLongitude()).thenReturn(-46.0);
        when(mockTrackPoint2.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint2);

        List<TrackPoint4Alg> result = dataCleaner.cleanData(input);
        assertEquals(2, result.size());
        assertEquals(45.0, result.get(0).getLatitude());
        assertEquals(46.0, result.get(1).getLatitude());
    }

    @Test
    public void testCleanDataWithInvalidLatitude() throws Exception {
        List<TrackPoint4Alg> input = new ArrayList<>();
        when(mockTrackPoint1.getLatitude()).thenReturn(91.0);
        when(mockTrackPoint1.getLongitude()).thenReturn(-45.0);
        when(mockTrackPoint1.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint1);

        when(mockTrackPoint2.getLatitude()).thenReturn(46.0);
        when(mockTrackPoint2.getLongitude()).thenReturn(-46.0);
        when(mockTrackPoint2.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint2);

        List<TrackPoint4Alg> result = dataCleaner.cleanData(input);
        assertEquals(1, result.size());
        assertEquals(46.0, result.get(0).getLatitude());
    }

    @Test
    public void testCleanDataWithInvalidLongitude() throws Exception {
        List<TrackPoint4Alg> input = new ArrayList<>();
        when(mockTrackPoint1.getLatitude()).thenReturn(45.0);
        when(mockTrackPoint1.getLongitude()).thenReturn(-181.0);
        when(mockTrackPoint1.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint1);

        when(mockTrackPoint2.getLatitude()).thenReturn(46.0);
        when(mockTrackPoint2.getLongitude()).thenReturn(-46.0);
        when(mockTrackPoint2.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint2);

        List<TrackPoint4Alg> result = dataCleaner.cleanData(input);
        assertEquals(1, result.size());
        assertEquals(46.0, result.get(0).getLatitude());
    }

    @Test
    public void testCleanDataWithInvalidAltitude() throws Exception {
        List<TrackPoint4Alg> input = new ArrayList<>();
        when(mockTrackPoint1.getLatitude()).thenReturn(45.0);
        when(mockTrackPoint1.getLongitude()).thenReturn(-45.0);
        when(mockTrackPoint1.getAltitude()).thenReturn(-1.0);
        input.add(mockTrackPoint1);

        when(mockTrackPoint2.getLatitude()).thenReturn(46.0);
        when(mockTrackPoint2.getLongitude()).thenReturn(-46.0);
        when(mockTrackPoint2.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint2);

        List<TrackPoint4Alg> result = dataCleaner.cleanData(input);
        assertEquals(1, result.size());
        assertEquals(46.0, result.get(0).getLatitude());
    }

    @Test
    public void testCleanDataWithNaNValues() throws Exception {
        List<TrackPoint4Alg> input = new ArrayList<>();
        when(mockTrackPoint1.getLatitude()).thenReturn(Double.NaN);
        when(mockTrackPoint1.getLongitude()).thenReturn(-45.0);
        when(mockTrackPoint1.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint1);

        when(mockTrackPoint2.getLatitude()).thenReturn(46.0);
        when(mockTrackPoint2.getLongitude()).thenReturn(Double.NaN);
        when(mockTrackPoint2.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint2);

        when(mockTrackPoint3.getLatitude()).thenReturn(47.0);
        when(mockTrackPoint3.getLongitude()).thenReturn(-47.0);
        when(mockTrackPoint3.getAltitude()).thenReturn(Double.NaN);
        input.add(mockTrackPoint3);

        when(mockTrackPoint4.getLatitude()).thenReturn(48.0);
        when(mockTrackPoint4.getLongitude()).thenReturn(-48.0);
        when(mockTrackPoint4.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint4);

        List<TrackPoint4Alg> result = dataCleaner.cleanData(input);
        assertEquals(1, result.size());
        assertEquals(48.0, result.get(0).getLatitude());
    }

    @Test
    public void testCleanDataWithInconsistentTrajectory() throws Exception {
        List<TrackPoint4Alg> input = new ArrayList<>();
        when(mockTrackPoint1.getLatitude()).thenReturn(45.0);
        when(mockTrackPoint1.getLongitude()).thenReturn(-45.0);
        when(mockTrackPoint1.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint1);

        when(mockTrackPoint2.getLatitude()).thenReturn(46.0);
        when(mockTrackPoint2.getLongitude()).thenReturn(-46.0);
        when(mockTrackPoint2.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint2);

        when(mockTrackPoint3.getLatitude()).thenReturn(90.0);
        when(mockTrackPoint3.getLongitude()).thenReturn(-90.0);
        when(mockTrackPoint3.getAltitude()).thenReturn(1000.0);
        input.add(mockTrackPoint3);

        List<TrackPoint4Alg> result = dataCleaner.cleanData(input);
        assertEquals(2, result.size());
        assertEquals(45.0, result.get(0).getLatitude());
        assertEquals(46.0, result.get(1).getLatitude());
    }

    @Test
    public void testIsPointInconsistentWithTrajectory() throws Exception {
        List<TrackPoint4Alg> trajectory = new ArrayList<>();
        when(mockTrackPoint1.getLatitude()).thenReturn(45.0);
        when(mockTrackPoint1.getLongitude()).thenReturn(-45.0);
        when(mockTrackPoint1.getAltitude()).thenReturn(1000.0);
        trajectory.add(mockTrackPoint1);

        when(mockTrackPoint2.getLatitude()).thenReturn(46.0);
        when(mockTrackPoint2.getLongitude()).thenReturn(-46.0);
        when(mockTrackPoint2.getAltitude()).thenReturn(1000.0);
        trajectory.add(mockTrackPoint2);

        when(mockTrackPoint3.getLatitude()).thenReturn(90.0);
        when(mockTrackPoint3.getLongitude()).thenReturn(-90.0);
        when(mockTrackPoint3.getAltitude()).thenReturn(1000.0);
        boolean result = DataCleaner.isPointInconsistentWithTrajectory(mockTrackPoint3, trajectory);
        assertTrue(result);
    }

    @Test
    public void testIsPointConsistentWithTrajectory() throws Exception {
        List<TrackPoint4Alg> trajectory = new ArrayList<>();
        when(mockTrackPoint1.getLatitude()).thenReturn(45.0);
        when(mockTrackPoint1.getLongitude()).thenReturn(-45.0);
        when(mockTrackPoint1.getAltitude()).thenReturn(1000.0);
        trajectory.add(mockTrackPoint1);

        when(mockTrackPoint2.getLatitude()).thenReturn(46.0);
        when(mockTrackPoint2.getLongitude()).thenReturn(-46.0);
        when(mockTrackPoint2.getAltitude()).thenReturn(1000.0);
        trajectory.add(mockTrackPoint2);

        when(mockTrackPoint3.getLatitude()).thenReturn(47.0);
        when(mockTrackPoint3.getLongitude()).thenReturn(-47.0);
        when(mockTrackPoint3.getAltitude()).thenReturn(1000.0);
        boolean result = DataCleaner.isPointInconsistentWithTrajectory(mockTrackPoint3, trajectory);
        assertFalse(result);
    }

    @Test
    public void testCalculateDistance() throws Exception {
        when(mockTrackPoint1.getLatitude()).thenReturn(45.0);
        when(mockTrackPoint1.getLongitude()).thenReturn(-45.0);
        when(mockTrackPoint1.getAltitude()).thenReturn(1000.0);

        when(mockTrackPoint2.getLatitude()).thenReturn(46.0);
        when(mockTrackPoint2.getLongitude()).thenReturn(-46.0);
        when(mockTrackPoint2.getAltitude()).thenReturn(1000.0);

        double distance = DataCleaner.calculateDistance(mockTrackPoint1, mockTrackPoint2);
        assertTrue(distance > 0);
    }
}
