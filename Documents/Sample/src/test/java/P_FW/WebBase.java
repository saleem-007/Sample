package P_FW;

import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class WebBase extends BaseTest{
    public static WebElement getWebElement(WebElement element){
        WebDriverWait webDriverWait=new WebDriverWait(driver,Duration.ofSeconds(10));
        return webDriverWait.until(ExpectedConditions.visibilityOf(element));
    }
}
