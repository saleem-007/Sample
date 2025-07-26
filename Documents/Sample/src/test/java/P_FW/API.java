package P_FW;

import static io.restassured.RestAssured.given;

public class API {
    public static String baseUri="https://reqres.in/";
    public static String api="api";

    public static void main(String[] args) {
        sample();
    }
    public static void sample(){
        given().log().all().get(String.format(baseUri+"%s/users?page=2",api)).then().statusCode(200);
    }
    public static void sample2(){
        given().log().all().put(String.format(baseUri+"%s/users?page=2",api)).then().statusCode(200);
    }
}
