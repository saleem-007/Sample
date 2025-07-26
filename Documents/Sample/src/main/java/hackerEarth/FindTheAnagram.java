package hackerEarth;

import java.util.Arrays;

public class FindTheAnagram {
    public static void main(String[] args) {
        char [] str1="GeeksForGeeks".toCharArray();
        char [] str12="ForGeeksGeeks".toCharArray();
        if (anagram(str1,str12)){
            System.out.println("2 Strings are anagram");
        }else {
            System.out.println("2 Strings are not anagram");
        }
    }
    public static boolean anagram(char [] str1,char [] str2){
        Arrays.sort(str1);
        Arrays.sort(str2);
        if (str1.length!=str2.length){
            return false;
        }else {
            for (int i=0;i<str1.length;i++){
                if(str1[i]!=str2[i]){
                    return false;
                }
            }
            return true;
        }
    }
}
