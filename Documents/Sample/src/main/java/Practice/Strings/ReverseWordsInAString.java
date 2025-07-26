package Practice.Strings;

public class ReverseWordsInAString {
    public static void main(String[] args) {
        String str="hello world";
        String [] word=str.split(" ");
        String rev="";
        for (int i=word.length-1; i>=0 ; i-- ){
            rev+=word[i]+" ";
        }
        System.out.println(rev);
    }
}
