package Practice.Basic;

import java.util.Scanner;

public class PrimeOrNot {
    public static void main(String[] args) {
        Scanner scanner=new Scanner(System.in);
        int num=scanner.nextInt();
        boolean isPrime=true;
        if (num<=1){
            isPrime=false;
        }else {
            for (int i=2;i<=Math.sqrt(num);i++){
                if(num%i==0){
                    isPrime=false;
                    break;
                }
            }
        }
        if (isPrime){
            System.out.println("Number is prime number");
        }else {
            System.out.println("Number is not prime number");
        }
    }
}
