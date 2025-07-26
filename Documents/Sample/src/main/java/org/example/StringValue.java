package org.example;

public class StringValue {
    public static void main(String[] args) {
        String str="xpath: stay: in: peace";
        String [] split=str.split(": ");
        String value="";
        int length=split.length;

        if (split.length>1){
            for (int i = 1; i < length; i++) {
                if (length-1==i){
                    value+=split[i];
                }else {
                    value+=split[i] +": ";
                }
            }
        }else {
            value=split[1].replace("})","");
        }
        System.out.println(value);
    }
}
