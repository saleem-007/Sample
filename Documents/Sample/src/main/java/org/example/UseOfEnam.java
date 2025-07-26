package org.example;

public class UseOfEnam {
    enum locators {
        id, xpath, accessibility, name
    }

    public static void switchFunction(locators loc){
        switch (loc){
            case id:
                System.out.println("id");
                break;
            case xpath:
                System.out.println("xpath");
                break;
            case accessibility:
                System.out.println("accessibility");
                break;
        }
    }

    public static void main(String[] args) {
        switchFunction(locators.id);
    }

}
