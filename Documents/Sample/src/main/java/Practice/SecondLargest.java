package Practice;

import java.util.Arrays;

public class SecondLargest {
    public static void main(String[] args) {
        int [] arr={3,40,54,87,90};
        int n=arr.length;
        System.out.println(secondLarge3(arr,n));;
    }
    public static int secondLarge1(int [] arr,int size){
        for (int i =0;i <size;i++){
            for (int j=1;j<size-i;j++){
                if (arr[i]>arr[j]){
                    int temp=arr[i];
                    arr[i]=arr[j];
                    arr[j]=temp;
                }
            }
        }
        return arr[size-2];
    }

    public static int secondLarge2(int [] arr,int size){
        int firstLargest=Integer.MIN_VALUE;
        int secondLargest=Integer.MIN_VALUE;
        for (int i =0; i < size;i++){
            if (arr[i]>firstLargest){
                secondLargest=firstLargest;
                firstLargest=arr[i];
            } else if (arr[i]>secondLargest&&arr[i]!=firstLargest) {{
                secondLargest=arr[i];
            }
            }
        }
        return secondLargest;
    }

    public static int secondLarge3(int [] arr,int size){
        Arrays.sort(arr);
        return arr[size-2];
    }
}
