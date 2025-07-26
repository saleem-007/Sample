package org.example;

import java.text.SimpleDateFormat;
import java.util.Calendar;

public class Date {
    public static void main(String[] args) {
        String currentDay = "";
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DATE, 1);
        java.util.Date date = cal.getTime();
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("EE");
        currentDay = simpleDateFormat.format(date.getTime());
        System.out.println(currentDay);
    }
}
