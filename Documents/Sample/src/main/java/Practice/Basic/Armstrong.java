package Practice.Basic;

import java.util.Scanner;

public class Armstrong {
    public static void main(String[] args) {
        Scanner scanner=new Scanner(System.in);
        int num=scanner.nextInt();
        int originalNum=num;
        int sum=0;
        while (num!=0){
            int rem=num%10;
            sum=sum+rem*rem*rem;
            num=num/10;
        }
        if (originalNum==sum){
            System.out.println("Given number is armstrong");
        }else {
            System.out.println("Given number is not an armstrong");
        }

    }
}
