package Practice;

import java.util.Arrays;

public class ArraysToString {
    public static void main(String[] args) {
        char [] arr={'s','a','l','e','e','m'};
        String s=new String(arr);
        System.out.println(s);
        System.out.println(Arrays.toString(arr));
    }
}
