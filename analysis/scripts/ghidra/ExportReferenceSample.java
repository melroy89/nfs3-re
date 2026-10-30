// Reference-only exporter for the three addresses in recompilation-readiness.md.
// Run on an isolated saved project with -readOnly -noanalysis. Never imports or edits it.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.app.util.exporter.CppExporter;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.*;
import ghidra.program.model.pcode.XmlEncode;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import com.google.gson.GsonBuilder;

public class ExportReferenceSample extends GhidraScript {
 private String hash(byte[] b)throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b));}
 private void require(boolean ok,String why)throws Exception{if(!ok)throw new Exception(why);}
 public void run()throws Exception{
  String[] args=getScriptArgs();require(args.length==2,"Expected entry and new output directory");
  Map<String,String> expected=Map.of("00485c30","3543671c1408e9124a8dd6dfc3166f296390b768b8ea8ab881517b3c041b237f","004abd9c","27c7ce1baedc6282855c2aadecfdbee768f25db8649f66aa9caea4e94ba9677b","00518640","64b39b42ecef516f64ab5db044fa9028e0591d59af23f14583d393fbc4cd6b2c");
  String entry=args[0];require(expected.containsKey(entry),"Address is not in the three-function allowlist");
  Path out=Path.of(args[1]);Files.createDirectories(out);Path result=out.resolve(entry+".result.json");
  require(!Files.exists(result)&&!Files.exists(out.resolve(entry+".c"))&&!Files.exists(out.resolve(entry+".h")),"Refusing to overwrite an attempt");
  Map<String,Object> ledger=new LinkedHashMap<>();ledger.put("entry",entry);ledger.put("status","failure");long start=System.nanoTime();DecompInterface iface=null;
  try{
   require(currentProgram.getExecutableSHA256().equals("2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb"),"Wrong executable identity");
   require(currentProgram.getLanguageID().toString().equals("x86:LE:32:default")&&currentProgram.getCompilerSpec().getCompilerSpecID().toString().equals("windows"),"Wrong language/compiler");
   Function f=getFunctionAt(toAddr(entry));require(f!=null&&!f.isExternal()&&f.hasCustomVariableStorage(),"Missing local/custom-storage function");
   byte[] bytes=new byte[(int)f.getBody().getNumAddresses()];currentProgram.getMemory().getBytes(f.getEntryPoint(),bytes);String bodyHash=hash(bytes);require(bodyHash.equals(expected.get(entry)),"Body fingerprint mismatch");
   ledger.put("name",f.getName());ledger.put("body",f.getBody().toString());ledger.put("body_sha256",bodyHash);ledger.put("body_bytes",bytes.length);ledger.put("function_count",currentProgram.getFunctionManager().getFunctionCount());ledger.put("stack_purge",f.getStackPurgeSize());
   List<String> params=new ArrayList<>();for(Parameter p:f.getParameters())params.add(p.getName()+":"+p.getDataType()+":"+p.getVariableStorage());ledger.put("parameters",params);ledger.put("return",f.getReturn().getDataType()+":"+f.getReturn().getVariableStorage());
   DecompileOptions options=new DecompileOptions();options.setDefaultTimeout(30);options.setCommentStyle(DecompileOptions.CommentStyleEnum.CStyle);options.setWARNCommentIncluded(true);
   iface=new DecompInterface();iface.setOptions(options);require(iface.openProgram(currentProgram),"Decompiler open failed");iface.toggleSyntaxTree(true);
   XmlEncode xml=new XmlEncode();options.encode(xml,iface);byte[] effective=xml.toString().getBytes(StandardCharsets.UTF_8);Files.write(out.resolve(entry+".options.xml"),effective);ledger.put("effective_options_sha256",hash(effective));ledger.put("simplification_style",iface.getSimplificationStyle());
   DecompileResults dr=iface.decompileFunction(f,30,monitor);ledger.put("decompile_completed",dr.decompileCompleted());ledger.put("decompile_timeout",dr.isTimedOut());ledger.put("decompile_message",dr.getErrorMessage());
   if(dr.isTimedOut()){ledger.put("status","timeout");throw new Exception("Decompiler timed out");}
   require(dr.decompileCompleted()&&dr.getDecompiledFunction()!=null,"No completed decompiled function");
   require(dr.getErrorMessage()==null||dr.getErrorMessage().isEmpty(),"Decompiler diagnostic needs review: "+dr.getErrorMessage());
   require(!dr.getDecompiledFunction().getC().isBlank(),"Empty preflight function body");
   iface.dispose();iface=null;
   CppExporter exporter=new CppExporter(options,true,true,false,true,true,"");
   boolean ok=exporter.export(out.resolve(entry+".c").toFile(),currentProgram,new AddressSet(f.getBody()),monitor);ledger.put("exporter_return",ok);ledger.put("exporter_log",exporter.getMessageLog().toString());require(ok,"Exporter returned failure");
   Map<String,Object> artifacts=new LinkedHashMap<>();for(String suffix:new String[]{".c",".h"}){Path file=out.resolve(entry+suffix);require(Files.isRegularFile(file)&&Files.size(file)>0,"Missing/empty "+suffix);byte[] content=Files.readAllBytes(file);require(!new String(content,StandardCharsets.UTF_8).contains("Unable to decompile"),"Exporter emitted failure placeholder");artifacts.put(entry+suffix,Map.of("bytes",content.length,"sha256",hash(content)));}
   ledger.put("artifacts",artifacts);ledger.put("status","success");
  }catch(Exception e){ledger.put("error",e.toString());println("REFERENCE_EXPORT_FAILURE "+entry+" "+e);}
  finally{if(iface!=null)iface.dispose();ledger.put("elapsed_seconds",(System.nanoTime()-start)/1e9);Files.writeString(result,new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create().toJson(ledger)+"\n",StandardCharsets.UTF_8);}
  println("REFERENCE_EXPORT_RESULT "+entry+" "+ledger.get("status"));
 }
}
