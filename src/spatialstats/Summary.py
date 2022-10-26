
import pickle,pandas
import os,json,argparse
import numpy as np

#*****for legacy - to get the right order
temp_samples= [
         "COVID_COVID_SAMPLE_16_ROI_3_ROI_3",
          "COVID_COVID_SAMPLE_8_ROI_3_ROI_3",
          "COVID_COVID_SAMPLE_19_ROI_1_ROI_1",
          "COVID_COVID_SAMPLE_16_ROI_1_ROI_1",
          "COVID_COVID_SAMPLE_10_ROI_2_ROI_2",
          "COVID_COVID_SAMPLE_8_ROI_1_ROI_1",
          "COVID_COVID_SAMPLE_10_ROI_3_ROI_3",
          "COVID_COVID_SAMPLE_11_ROI_2_ROI_2",
          "COVID_COVID_SAMPLE_11_ROI_1_ROI_1",
          "COVID_COVID_SAMPLE_4_ROI_3_ROI_3",
          "COVID_COVID_SAMPLE_9_ROI_2_ROI_2",
          "COVID_COVID_SAMPLE_4_ROI_2_ROI_2",
          "COVID_COVID_SAMPLE_20_ROI_2_ROI_2",
          "COVID_COVID_SAMPLE_19_ROI_2_ROI_2",
          "COVID_COVID_SAMPLE_9_ROI_1_ROI_1",
          "COVID_COVID_SAMPLE_14_ROI_2_ROI_2",
          "COVID_COVID_SAMPLE_5_ROI_3_ROI_3",
          "COVID_COVID_SAMPLE_17_ROI_1_ROI_1",
          "COVID_COVID_SAMPLE_5_ROI_1_ROI_1",
          "COVID_COVID_SAMPLE_14_ROI_1_ROI_1",
          "COVID_COVID_SAMPLE_20_ROI_17_ROI_17",
          "COVID_COVID_SAMPLE_17_ROI_2_ROI_2",
          "COVID_COVID_SAMPLE_5_ROI_2_ROI_2",
          "COVID_COVID_SAMPLE_6_ROI_3_ROI_3",
          "HC_HEALTHY_SAMPLE_1_ROI_2_ROI_2",
          "COVID_COVID_SAMPLE_17_ROI_3_ROI_3",
          "HC_HEALTHY_SAMPLE_2_ROI_1_ROI_1",
          "HC_HEALTHY_SAMPLE_2_ROI_2_ROI_2",
          "COVID_COVID_SAMPLE_6_ROI_1_ROI_1",
          "COVID_COVID_SAMPLE_6_ROI_2_ROI_2",
          "HC_HEALTHY_SAMPLE_1_ROI_1_ROI_1",
          "COVID_COVID_SAMPLE_17_ROI_4_ROI_4"
]



#gets a pickle file and checks it exists
# id to cluster cl01:0 etc
def get_network_stats(sample_id,pickle_file,data,id_to_cluster):
    x=pickle_file
    cl_length= len(id_to_cluster)
    cellnumbers=[0] * cl_length
    for cl in x["outputs"]:
        index=0
        cellsn=[0] * cl_length
        
        n_cells=  len(x["outputs"][cl]["degree"])
        cellnumbers[id_to_cluster[cl]]=n_cells
        n_surrounding_cells= sum(x["outputs"][cl]["degree"])
        for ncells in x["outputs"][cl]["degree"]:
            neighbours = x["outputs"][cl]["neighbourTypesAsInts"][index:index+ncells]
            incontact=[False]*cl_length
            for n in neighbours:
                incontact[n]=True
            for i,n in enumerate(incontact):
                if n:
                    cellsn[i]+=1
            index+=ncells

        for i,v in enumerate(cellsn):
            ntw= x["outputs"][cl]["hist"][i]
            item = data["{}|{}|{}".format(sample_id,id_to_cluster[cl],i)] 
            item["contacts"]=v
            item["%contacts"]= (v/n_cells)*100
            item["Network"]=ntw
            item["Network(%)"]= (ntw/n_surrounding_cells)*100
            item["mean degree"]= ntw/n_cells

    #now add cell numbers and fill in blanks
    for n in range(cl_length):
        for i in range(cl_length):
            key = "{}|{}|{}".format(sample_id,n,i)
            item = data.get(key)
            for k in ["contacts","%contacts","Network","Network(%)","mean degree"]:
                if item.get(k) == None:
                    item[k]=0    
            item["cell 1 number"]=cellnumbers[n]
            item["cell 2 number"]=cellnumbers[i]      


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-p', '--pathToData', 
        help = 'Path to the base folder of the analysis',
        required = True
    )
    parser.add_argument(
        '-c', '--cluster_annotations', 
        help = 'Input file with cluster annotations.',
        required = True
    )

    parser.add_argument(
        '-a', '--alternative_annotations', 
		help = 'Actual names to write to file',
        required = False
    ) 
    parser.add_argument(
        '-o', '--output', 
		help = 'Path to write all the outputs to.',
        required = True
    ) 
    
 
   
    args = parser.parse_args()

  

    base_folder= args.pathToData
    outputdir= args.output

    df= pandas.read_csv(args.cluster_annotations,sep="\t")
    clusters= list(df.Annotation)
    names_to_write =clusters
    if args.alternative_annotations:
        df= pandas.read_csv(args.alternative_annotations,sep="\t")
        names_to_write=list(df.Annotation)

    id_to_cluster={"cl0"+str(n+1) if n<9 else "cl"+str(n+1):n for n,v in enumerate(clusters) }

    #get the samples from the quadrat methods folder
    samples = [ x.replace("_quadratCounts_data.p","") for x in os.listdir(os.path.join(base_folder,"quadratMethods"))]

    #*****************legacy
    samples= temp_samples
    #*****************legacy

    data= {}
    for sample in samples:
        for c1 in range(0,len(clusters)):
            for c2 in range(0,len(clusters)):
                data["{}|{}|{}".format(sample,c1,c2)]={}

   


    #methods for to get data from each pickle file
    def addNetwork(sample,x):
       get_network_stats(sample,x,data,id_to_cluster)


    def addMH(sample,x):
        l = x["nSpecies"]
        sp= x["clusterNames_MH"]
        C_O_plot = x["C_O"] + 2*np.identity(l)
        for n in range(len(clusters)):
            for i in range(len(clusters)):
                item= data["{}|{}|{}".format(sample,n,i)]
                item["MH_SES"]=None
                item["MH_PC"]=None
                item["MH_FDR"]=None

        for n in range(0,l):
            for i in range(0,l):
                cl1 = clusters.index(str(sp[n]))
                cl2 = clusters.index(str(sp[i])) 
                item= data["{}|{}|{}".format(sample,cl1,cl2)]  
                item["MH_SES"]= (x["C_O"][n,i] - np.mean(x["C_ns"][:,n,i])) / np.std(x["C_ns"][:,n,i])
                item["MH_PC"]=C_O_plot[n,i]
                item["MH_FDR"]= x["p_star"][n,i]

    def addQCounts(sample,x):
        l = len(clusters)
        for n in range(0,l):
            for i in range(0,l):
                data["{}|{}|{}".format(sample,n,i)]["quadratCounts"]=x["r"][n][i]
        
    pcf_radii=[10,20]
    def addPCF(sample,x):
        l = len(clusters)
        radii= list(x["radii"])
        rindexes= list(map(lambda x: radii.index(x),pcf_radii))
        for n in range(0,l):
            for i in range(0,l):
                for r in range(0,len(pcf_radii)):
                    v= None
                    #missing values not 0
                    if not x["gs"][n][i].max()==0:
                        try:
                            v=x["gs"][n][i][rindexes[r]]
                        except:
                            v=None
                    else:
                        print("None")
                    data["{}|{}|{}".format(sample,n,i)]["gr{}".format(pcf_radii[r])]=v

    #dict of methods
    analysis= [
        {
            "file":"MoruetaHolme_data.p",
            "method":addMH,
            "subfolder":"morueta-holme"
        },

        {
            "file":"networkAnalysis_data.p",
            "method":addNetwork,
            "subfolder":"networkstatistics"
        },
        {
            "file":"quadratCounts_data.p",
            "method":addQCounts,
            "subfolder":"quadratMethods"
        },
        {
            "file":"PCF_data.p",
            "method":addPCF,
            "subfolder":"paircorrelationfunction"
        }
    ]

#go through each sample and extract data from each pickle file
    for sample in samples:
        for a in analysis:
            pickle_file= os.path.join(base_folder,a["subfolder"],f'{sample}_{a["file"]}')
            if not os.path.exists(pickle_file):
                print(f'{pickle_file} does not exist')
                continue
            with open (pickle_file,"rb") as f:
                a["method"](sample,pickle.load(f))
        
   

#copy the PCF images and add unique id to the data object
    key_index=0

    images_zip = os.path.join(outputdir,"images.zip")
    lhm_images_zip = os.path.join(outputdir,"images_lhm.zip")

    #zip_file = zipfile.ZipFile(images_zip, 'w')
    #zip_file_lhm = zipfile.ZipFile(lhm_images_zip, 'w')
    al = set()

    for sample in samples:
       
        for i1,c1 in enumerate(clusters):
            for i2,c2 in enumerate(clusters):
                im ="{}_{} to {}_PCF.png".format(sample,c1,c2)
                im2 = "{}_{} to {}_localClusteringHeatmap.png".format(sample,c1,c2)
                if im in al:
                    print(im)
                al.add(im) 
                f= os.path.join(base_folder,"paircorrelationfunction",im)
                if not os.path.exists(f):
                    print("{} does not exist".format(im))
                    continue
                f2  = os.path.join(base_folder,"localclusteringheatmaps",im2)
                if not os.path.exists(f2):
                    print("{} does not exist".format(im2))
                    continue
                data["{}|{}|{}".format(sample,i1,i2)]["PCF_image"]=key_index
                data["{}|{}|{}".format(sample,i1,i2)]["LCH_image"]=key_index
                #zip_file.write(f,arcname="im{}.png".format(key_index), compress_type=zipfile.ZIP_DEFLATED)
                #zip_file_lhm.write(f2,arcname="im{}.png".format(key_index), compress_type=zipfile.ZIP_DEFLATED)
                key_index+=1
        

    #zip_file.close()
    #zip_file_lhm.close()




    # save the data to a flat file
    o = open(os.path.join(outputdir,"data.txt"),"w")
    headers=["sample_id","condition","ROI","sample_name","Cell Type 1","Cell Type 2",
                "cell 1 number","cell 2 number",
                "MH_FDR","MH_PC","MH_SES",
                "contacts","%contacts","Network","Network(%)","mean degree",
                "quadratCounts","PCF_image","LCH_image"]
    for r in pcf_radii:
        headers.append("gr{}".format(r))
 
    o.write("\t".join(headers)+"\n")

    for k in data:
        arr= k.split("|")
        sample_id=arr[0]
        
        cds = sample_id.split("_")
        #legacy******************
        cds=cds[1:-2]
        #*********************
        

       

        condition = cds[0]
        #legacy******************
        if condition == "HEALTHY":
            condition="HC"
        #*********************

      
        sample_name="_".join(cds[0:3])
        ROI ="_".join(cds[-2:])
        c1=names_to_write[int(arr[1])]
        c2=names_to_write[int(arr[2])]
        row= data[k]
        o.write("{}\t{}\t{}\t{}\t{}\t{}".format("_".join(cds),condition,ROI,sample_name,c1,c2))
        for h in headers[6:]:
            o.write("\t"+str(row.get(h,None)))
        o.write("\n")
        
        
        


    o.close()

    #write out the config
    columns=[]
    for c,h in enumerate(headers,start=1):
        dt= "text"
        if c>6:
            dt = "double"
        columns.append({
            "name":h,
            "order":c,
            "datatype":dt

        })
    columns[4]["values"]=names_to_write
    columns[5]["values"]=names_to_write
    conf= {"columns":columns}
    o = open(os.path.join(outputdir,"config.json"),"w")
    o.write(json.dumps(conf))
    o.close()

if __name__ == "__main__":
  
    main()
    df1 = pandas.read_csv("/t1-data/project/covidhyperion/sergeant/tests/data.txt",sep="\t")
    df2 = pandas.read_csv("/t1-data/project/covidhyperion/shared/data/panel2/tree/COVID_HC_spatialstats/iteration4_v1/summary_ROI/all_data.txt",sep="\t")
    df1["PCF_image"]= df2["PCF_image"]
    df1["LCH_image"]= df2["LCH_image"]
    df1.to_csv("/t1-data/project/covidhyperion/sergeant/tests/data1.txt",sep="\t",index=False)