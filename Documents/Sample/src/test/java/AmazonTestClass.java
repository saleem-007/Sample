import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class AmazonTestClass {
    WebDriver driver;
    @BeforeMethod
    public void setUp() throws InterruptedException {
        WebDriverManager.chromedriver().setup();
        driver=new ChromeDriver();
        driver.manage().window().fullscreen();
        driver.get("https://www.amazon.in");
        Thread.sleep(2000);
    }
    @AfterMethod
    public void tearDown(){
        if (driver!=null){
            driver.quit();
        }
    }

    @Test
    public void verifyTheCheckBoxClickingOrNot() throws InterruptedException {
        driver.findElement(By.id("twotabsearchtextbox")).click();
        driver.findElement(By.id("twotabsearchtextbox")).sendKeys("headphones bluetooth wireless");
        driver.findElement(By.xpath("//input[contains(@id,'submit')]")).click();
        Thread.sleep(2000);
        driver.findElement(By.xpath("//span[@class='rush-component']//div[@id='brandsRefinements']//span[text()='JBL']/preceding-sibling::div")).click();
    }
}
