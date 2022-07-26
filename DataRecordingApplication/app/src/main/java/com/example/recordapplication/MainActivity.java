package com.example.recordapplication;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Build;
import android.os.Bundle;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;

import android.view.View;

import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;

public class MainActivity extends AppCompatActivity implements SensorEventListener, View.OnClickListener{
    private SensorManager sensorManager;
    private Sensor accelerometer, gyroscope, magnetometer;

    private String record = "";
    private float lastAccX, lastAccY, lastAccZ;
    private float lastGyrX, lastGyrY, lastGyrZ;
    private float lastMagX, lastMagY, lastMagZ;
    String Label = "GAIT";

    TextView currentRecord;

    @RequiresApi(api = Build.VERSION_CODES.M)
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initializeViews();
        sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        if (sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER) != null) {
            accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        }
        if (sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE) != null) {
            gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        }
        if (sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD) != null) {
            magnetometer = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
        }
        sensorManager = null;
    }

    @Override
    public void onClick(View v){
        if(v.getId() == R.id.startStep) {
            Label = "STEP";
            if(sensorManager == null) {
                sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
                sensorManager.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_FASTEST);
                sensorManager.registerListener(this, gyroscope, SensorManager.SENSOR_DELAY_FASTEST);
                sensorManager.registerListener(this, magnetometer, SensorManager.SENSOR_DELAY_FASTEST);
                Toast.makeText(getBaseContext(), "Starting the step recording ", Toast.LENGTH_LONG).show();
            }
        } else if(v.getId() == R.id.startRamp){
            Label = "RAMP";
            if(sensorManager == null) {
                sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
                sensorManager.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_FASTEST);
                sensorManager.registerListener(this, gyroscope, SensorManager.SENSOR_DELAY_FASTEST);
                sensorManager.registerListener(this, magnetometer, SensorManager.SENSOR_DELAY_FASTEST);
                Toast.makeText(getBaseContext(), "Starting the ramp recording", Toast.LENGTH_LONG).show();
            }
        }  else if(v.getId() == R.id.startUnevenZone){
            Label = "UNEVEN";
            if(sensorManager == null) {
                sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
                sensorManager.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_FASTEST);
                sensorManager.registerListener(this, gyroscope, SensorManager.SENSOR_DELAY_FASTEST);
                sensorManager.registerListener(this, magnetometer, SensorManager.SENSOR_DELAY_FASTEST);
                Toast.makeText(getBaseContext(), "Starting the uneven zone recording", Toast.LENGTH_LONG).show();
            }
        } else if(v.getId() == R.id.startGait){
            Label = "GAIT";
            if(sensorManager == null) {
                sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
                sensorManager.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_FASTEST);
                sensorManager.registerListener(this, gyroscope, SensorManager.SENSOR_DELAY_FASTEST);
                sensorManager.registerListener(this, magnetometer, SensorManager.SENSOR_DELAY_FASTEST);
                Toast.makeText(getBaseContext(), "Starting the gait recording", Toast.LENGTH_LONG).show();
            }
        } else if(v.getId() == R.id.stop){
            if(sensorManager != null) {
                sensorManager.unregisterListener(this);
                sensorManager = null;
                displayCleanValues();
                Toast.makeText(getBaseContext(), "Stopping the recording", Toast.LENGTH_LONG).show();
            }
        }
    }

    public void initializeViews() {
        currentRecord = findViewById(R.id.currentRecord);
        Button button = findViewById(R.id.startGait);
        button.setOnClickListener(this);
        button = findViewById(R.id.startStep);
        button.setOnClickListener(this);
        button = findViewById(R.id.startRamp);
        button.setOnClickListener(this);
        button = findViewById(R.id.startUnevenZone);
        button.setOnClickListener(this);
        button = findViewById(R.id.stop);
        button.setOnClickListener(this);
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {

    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if(event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
            lastAccX = event.values[0];
            lastAccY = event.values[1];
            lastAccZ = event.values[2];
        } else if(event.sensor.getType() == Sensor.TYPE_GYROSCOPE){
            lastGyrX = event.values[0];
            lastGyrY = event.values[1];
            lastGyrZ = event.values[2];
        } else if(event.sensor.getType() == Sensor.TYPE_MAGNETIC_FIELD){
            lastMagX = event.values[0];
            lastMagY = event.values[1];
            lastMagZ = event.values[2];
        } else return;
        String timestamp = new SimpleDateFormat("yyyy/MM/dd-HH:mm:ss.SSS").format(new java.util.Date());
        record = timestamp + ","+ lastAccX + "," + lastAccY + "," + lastAccZ + "," + lastGyrX + "," + lastGyrY + "," + lastGyrZ + "," + lastMagX + "," + lastMagY + "," + lastMagZ + "," + Label;
        displayCurrentRecord();
        writeToFile(record);
    }

    public void displayCleanValues() {
        currentRecord.setText("");
    }

    public void displayCurrentRecord() {
        currentRecord.setText(record);
    }

    public void writeToFile(String content){
        content += '\n';
        File path = getApplicationContext().getFilesDir();
        try {
            FileOutputStream writer = new FileOutputStream(new File(path,"data.csv"), true);
            writer.write(content.getBytes());
            writer.close();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}