package P_FW;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;

public class LoginPage extends WebBase{
    public LoginPage(WebDriver driver1){
        driver=driver1;
        PageFactory.initElements(driver1,this);
    }
    @FindBy(xpath = "")
    public WebElement userName;
}
