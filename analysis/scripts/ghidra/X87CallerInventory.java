import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.util.*;
import java.nio.file.*;
import com.google.gson.*;
public class X87CallerInventory extends GhidraScript {
 public void run()throws Exception{
 Map<String,Object> root=new LinkedHashMap<>();root.put("executable_sha256",currentProgram.getExecutableSHA256());List<Object> funcs=new ArrayList<>();
 for(String s:new String[]{"00485c30","00485f20","004860b0","004873e0","00487a30","0049bf40","00486f70","004870c0","0048d4c0","0048a206"}){
 Function f=getFunctionContaining(toAddr(s));Map<String,Object> fn=new LinkedHashMap<>();fn.put("entry",f.getEntryPoint().toString());fn.put("name",f.getName());fn.put("body",f.getBody().toString());List<String> refs=new ArrayList<>();ReferenceIterator r=currentProgram.getReferenceManager().getReferencesTo(f.getEntryPoint());while(r.hasNext())refs.add(r.next().toString());fn.put("incoming",refs);
 List<Object> ins=new ArrayList<>();InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);while(it.hasNext()){Instruction i=it.next();Map<String,Object> m=new LinkedHashMap<>();m.put("address",i.getAddress().toString());m.put("text",i.toString());m.put("mnemonic",i.getMnemonicString());m.put("length",i.getLength());m.put("fallthrough",i.getFallThrough()==null?null:i.getFallThrough().toString());List<String> flows=new ArrayList<>();for(var a:i.getFlows())flows.add(a.toString());m.put("flows",flows);m.put("flow_type",i.getFlowType().toString());ins.add(m);}fn.put("instructions",ins);funcs.add(fn);
 }
 root.put("functions",funcs);Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(root)+"\n");println("X87_CALLER_INVENTORY_OK functions="+funcs.size());
 }
}
