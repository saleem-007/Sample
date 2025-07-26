package SampleTests;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class TestClass {
    WebDriver driver;
    @BeforeMethod
    public void setUp() throws InterruptedException {
        WebDriverManager.chromedriver().setup();
        driver=new ChromeDriver();
        driver.get("https://demo.automationtesting.in/Register.html");
        driver.manage().window().fullscreen();
    }
    @Test
    public void test1() throws InterruptedException {
        Thread.sleep(1000);
        driver.findElement(By.xpath("//input[contains(@placeholder,'First Name')]")).sendKeys("Saleem");
        Thread.sleep(1000);
        driver.findElement(By.xpath("//input[@value='Male']")).click();
    }

}
