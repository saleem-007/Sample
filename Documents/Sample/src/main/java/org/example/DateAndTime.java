package org.example;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;

public class DateAndTime {

    public static void main(String[] args) {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime hours = now.plus(1, ChronoUnit.HOURS);
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("HH:mm");
        String formattedDateTime = hours.format(formatter);
        System.out.println("Current time plus one day: " + formattedDateTime);
    }
}
