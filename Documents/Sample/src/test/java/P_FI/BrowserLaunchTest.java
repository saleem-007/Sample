package P_FI;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.support.ui.Select;
import org.testng.Assert;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.time.Duration;

public class BrowserLaunchTest {
    WebDriver driver;
    @BeforeMethod
    public void setup() throws InterruptedException {
        WebDriverManager.chromedriver().setup();
        driver=new ChromeDriver();
        driver.get("https://www.google.co.in/");
        Thread.sleep(2000);
    }

    @Test
    public void test1(){
        String currentURL= driver.getCurrentUrl();
        System.out.println(currentURL);
        Assert.assertTrue(currentURL.contains("google"));
        driver.getTitle();
        driver.manage().window().fullscreen();
//        driver.getPageSource();
//        driver.get("");
//        driver.close();
//        driver.quit();
//        driver.findElement();
        System.out.println(driver.getWindowHandle());;
        driver.manage().timeouts().implicitlyWait(Duration.ofMillis(2));
        driver.quit();
        WebElement element=driver.findElement(By.xpath(""));

        JavascriptExecutor js= (JavascriptExecutor) driver;
        js.executeScript("arguments[0].click();",driver.findElement(By.xpath("")));

        Select select=new Select(element);
        select.selectByIndex(0);
        select.selectByValue("value");
        select.selectByVisibleText("visible text");

            Actions action=new Actions(driver);
            action.moveToElement(element).perform();


    };
}
