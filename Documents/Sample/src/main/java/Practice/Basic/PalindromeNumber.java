package Practice.Basic;

import java.util.Scanner;

public class PalindromeNumber {
    public static void main(String[] args) {
        Scanner scanner=new Scanner(System.in);
        int num=scanner.nextInt();
        int on=num;
        int rotatedNUm=0;
        while (num!=0){
            int rem=num%10;
            rotatedNUm=rotatedNUm*10+rem;
            num/=10;
        }
        if (rotatedNUm==on){
            System.out.println("number is palindrome");
        }else {
            System.out.println("number is not a 1palindrome");
        }
    }
}
