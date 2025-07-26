package Practice.Strings;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;

public class PatternCompression {
    public static void main(String[] args) {
        String str1="aaabbc";
        String str2="";
        ArrayList<Character> ar=new ArrayList<>();
        HashMap<Character, Integer> hm=new HashMap<>();
        for (int i =0; i<str1.length(); i++){
            if (ar.contains(str1.charAt(i))){
                int count=hm.get(str1.charAt(i));
                hm.put(str1.charAt(i),count+1);
            }else{
                ar.add(str1.charAt(i));
                hm.put(str1.charAt(i),1);
            }
        }
        for (char c: ar){
            str2=str2+c+hm.get(c);
        }
        System.out.println(str2);
    }
}
