package hackerEarth;

import java.util.*;

public class SortTheSquares {
    public static void main(String[] args) {
        int [] arr={-4,-1,0,3,10};
        System.out.println(sortTheArray(arr, arr.length));;
    }
    public static List<Integer> sortTheArray(int [] arr,int size){

        List<Integer> res=new ArrayList<>();
        for (int i =0;i<size;i++){
           res.add(arr[i]*arr[i]);
        }
        Collections.sort(res);
        return res;
    }
}
