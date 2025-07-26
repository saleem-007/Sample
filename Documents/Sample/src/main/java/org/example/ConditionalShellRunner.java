package org.example;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.concurrent.TimeUnit;

public class ConditionalShellRunner {
    public static void main(String[] args) {
        try {
            String scriptPath = "src/main/resources/startup-script.sh";

            // Check if script is already running
            String checkCommand = "pgrep -f " + scriptPath;
            Process checkProcess = Runtime.getRuntime().exec(new String[]{"bash", "-c", checkCommand});

            BufferedReader checkReader = new BufferedReader(new InputStreamReader(checkProcess.getInputStream()));
            String line = checkReader.readLine();

            if (line != null && !line.isEmpty()) {
                System.out.println("Script is already running. Skipping execution.");
            } else {
                System.out.println("Script is not running. Executing now...");

                ProcessBuilder pb = new ProcessBuilder("bash", scriptPath);
                pb.redirectErrorStream(true);
                Process process = pb.start();

                // Start a thread to read output asynchronously
                new Thread(() -> {
                    try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                        String outputLine;
                        while ((outputLine = reader.readLine()) != null) {
                            System.out.println(outputLine);
                        }
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }).start();

                // Wait for at most 30 seconds
                boolean finished = process.waitFor(30, TimeUnit.SECONDS);

                if (!finished) {
                    System.out.println("Script timed out. Destroying process...");
                    process.destroyForcibly();
                } else {
                    int exitCode = process.exitValue();
                    System.out.println("Script executed with exit code: " + exitCode);
                }
            }

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }

}
