package P_FW;

import io.github.bonigarcia.wdm.WebDriverManager;
import io.qameta.allure.Allure;
import lombok.extern.slf4j.Slf4j;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.ITestResult;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;

import java.io.ByteArrayInputStream;

@Slf4j
public class BaseTest {
    public static WebDriver driver;
    @BeforeMethod(alwaysRun = true)
    public void setUp(){
        WebDriverManager.chromedriver().clearDriverCache().setup();
        driver=new ChromeDriver();
        driver.manage().window().fullscreen();
        driver.get("");
       // log.info("Driver has successfully launch the base url");
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown(ITestResult context){
        if (context.getStatus()==ITestResult.FAILURE || context.getStatus()==ITestResult.SKIP){
            if (driver!=null){
                try{
                    Allure.addAttachment(context.getName(), new ByteArrayInputStream(((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES)));
                }catch (Exception e){
                    e.printStackTrace();
                }
            }
        }
        if (driver!=null){
            driver.quit();
        }
    }
}
