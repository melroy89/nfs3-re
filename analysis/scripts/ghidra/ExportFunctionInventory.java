// Read-only function/range inventory for address-based binary comparison.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import java.nio.file.*;
import java.util.*;
import com.google.gson.*;
public class ExportFunctionInventory extends GhidraScript {
 public void run()throws Exception{
 Map<String,Object> root=new LinkedHashMap<>();root.put("executable_sha256",currentProgram.getExecutableSHA256());root.put("language",currentProgram.getLanguageID().toString());root.put("compiler",currentProgram.getCompilerSpec().getCompilerSpecID().toString());List<Object> funcs=new ArrayList<>();FunctionIterator it=currentProgram.getFunctionManager().getFunctions(true);
 while(it.hasNext()){Function f=it.next();Map<String,Object> a=new LinkedHashMap<>();a.put("entry",f.getEntryPoint().toString());a.put("name",f.getName());a.put("thunk",f.isThunk());List<Object> ranges=new ArrayList<>();AddressRangeIterator ri=f.getBody().getAddressRanges();while(ri.hasNext()){AddressRange r=ri.next();ranges.add(List.of(r.getMinAddress().toString(),r.getMaxAddress().add(1).toString()));}a.put("ranges",ranges);funcs.add(a);}
 root.put("functions",funcs);root.put("local_count",funcs.size());Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(root)+"\n");println("FUNCTION_INVENTORY_OK local="+funcs.size());
 }
}
