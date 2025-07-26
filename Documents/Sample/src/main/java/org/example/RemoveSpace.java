package org.example;

public class RemoveSpace {
    public static void main(String[] args) {
        String str ="Vehicle Registration is  K A - 0 5 - M H - 9 8 7 9 , Vehicle id is A B C D   -   S A L 1 2 3 ,  , Cab trip";
        if (str.replace(" ","").contains("KA-05-MH-9879")){
            System.out.println("Yes i did it");
        }else {
            System.out.println("No, it failed and retry");
        }
    }
}
