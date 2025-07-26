import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class Testing {
    @BeforeMethod(onlyForGroups = "init")
    public void ini(){
        System.out.println("dude");
    }
    @Test(groups = "init")
    public void sample() throws InterruptedException {
        System.out.println("hello");
        Thread.sleep(3000);
    }
    @Test(dependsOnMethods = "sample")
    public void sa() throws InterruptedException {
        System.out.println("copy");
        Thread.sleep(4000);
    }
}
