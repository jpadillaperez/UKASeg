import os
import sys
import torch 
import torch.nn as nn
import numpy as np
import nibabel as nib
import argparse

#------------------------------------------------------------------------------------------
class SSEConv(nn.Module):
    def __init__(self, in_channel=1, out_channel1=1, out_channel2=2, stride=1, kernel_size=3, 
                 padding=1, dilation=1, down_sample=1, bias=True): 
        self.in_channel = in_channel
        self.out_channel = out_channel1
        super(SSEConv, self).__init__()
        self.conv1 = nn.Conv3d(in_channel, out_channel1, kernel_size, stride=stride, padding=padding*dilation, bias=bias, dilation=dilation)
        self.conv2 = nn.Conv3d(out_channel1, out_channel2, kernel_size=1, stride=1, padding=0, bias=bias)
        self.norm = nn.InstanceNorm3d(out_channel1)
        self.act = nn.LeakyReLU(inplace = True)
        self.up_sample = nn.Upsample(scale_factor=down_sample, mode='trilinear', align_corners=True)
        self.conv_se = nn.Conv3d(out_channel1, 1, kernel_size=1, stride=1, padding=0, bias=False)
        self.norm_se = nn.Sigmoid()
        
    def forward(self, x):
        e0 = self.conv1(x)
        e0 = self.norm(e0)
        e0 = self.act(e0)
        e_se = self.conv_se(e0)
        e_se = self.norm_se(e_se)
        e0 = e0 * e_se
        e1 = self.conv2(e0)
        e1 = self.up_sample(e1)
        return e0, e1
    
class SSEConv2(nn.Module):
    def __init__(self, in_channel=1, out_channel1=1, out_channel2=2, stride=1, kernel_size=3, 
                 padding=1, dilation=1, down_sample=1, bias=True): 
        self.in_channel = in_channel
        self.out_channel = out_channel1
        super(SSEConv2, self).__init__()
        self.conv1 = nn.Conv3d(in_channel, out_channel1, kernel_size, stride=stride, padding=padding*dilation, bias=bias, dilation=dilation)
        self.conv2 = nn.Conv3d(out_channel1, out_channel2, kernel_size=1, stride=1, padding=0, bias=bias)
        self.norm = nn.InstanceNorm3d(out_channel1)
        self.act = nn.LeakyReLU(inplace = True)
        self.up_sample = nn.Upsample(scale_factor=down_sample, mode='trilinear', align_corners=True)
        self.conv_se = nn.Conv3d(out_channel1, 1, kernel_size=1, stride=1, padding=0, bias=False)
        self.norm_se = nn.Sigmoid()
        self.conv_se2 = nn.Conv3d(out_channel1, 1, kernel_size=1, stride=1, padding=0, bias=False)
        self.norm_se2 = nn.Sigmoid()
    
    def forward(self, x):
        e0 = self.conv1(x)
        e0 = self.norm(e0)
        e0 = self.act(e0)
        e_se = self.conv_se(e0)
        e_se = self.norm_se(e_se)
        e0 = e0 * e_se
        e_se = self.conv_se2(e0)
        e_se = self.norm_se2(e_se)
        e0 = e0 * e_se
        e1 = self.conv2(e0)
        e1 = self.up_sample(e1)
        return e0, e1
    
    
class droplayer(nn.Module):
    def __init__(self, channel_num=1, thr = 0.3):
        super(droplayer, self).__init__()
        self.channel_num = channel_num
        self.threshold = thr
    def forward(self, x):
        if self.training:
            r = torch.rand(x.shape[0],self.channel_num,1,1,1).cuda()
            r[r<self.threshold] = 0
            r[r>=self.threshold] = 1
            r = r*self.channel_num/(r.sum()+0.01)
            return x*r
        else:
            return x
    

    
class WingsNet(nn.Module):
    def __init__(self, in_channel=1, n_classes=1):
        self.in_channel = in_channel
        self.n_classes = n_classes
        self.batchnorm = False
        self.bias = True
        self.out_channel2 = 2
        super(WingsNet, self).__init__()
        self.ec1 = SSEConv(self.in_channel, 8, self.out_channel2, bias=self.bias)
        self.ec2 = SSEConv(8, 16, self.out_channel2, bias=self.bias)
        self.ec3 = SSEConv(16, 32, self.out_channel2, bias=self.bias, dilation=2)
        
        self.ec4 = SSEConv2(32, 32, self.out_channel2, bias=self.bias, down_sample=2)
        self.ec5 = SSEConv2(32, 32, self.out_channel2, bias=self.bias, dilation=2, down_sample=2)
        self.ec6 = SSEConv2(32, 64, self.out_channel2, bias=self.bias, dilation=2, down_sample=2)
        
        self.ec7 = SSEConv2(64, 64, self.out_channel2, bias=self.bias, down_sample=4)
        self.ec8 = SSEConv2(64, 64, self.out_channel2, bias=self.bias, dilation=2, down_sample=4)
        self.ec9 = SSEConv2(64, 64, self.out_channel2, bias=self.bias, dilation=2, down_sample=4)
        
        self.ec10 = SSEConv2(64, 64, self.out_channel2, bias=self.bias, down_sample=8)
        self.ec11 = SSEConv2(64, 64, self.out_channel2, bias=self.bias, down_sample=8)
        self.ec12 = SSEConv2(64, 64, self.out_channel2, bias=self.bias, down_sample=8)
        
        
        self.pool0 = nn.MaxPool3d(kernel_size=[2,2,2],stride=[2,2,2],return_indices =False)
        self.pool1 = nn.MaxPool3d(kernel_size=[2,2,2],stride=[2,2,2],return_indices =False)
        self.pool2 = nn.MaxPool3d(kernel_size=[2,2,2],stride=[2,2,2],return_indices =False)
        
        self.up_sample0 = nn.Upsample(scale_factor=2, mode='trilinear', align_corners=True)
        self.up_sample1 = nn.Upsample(scale_factor=2, mode='trilinear', align_corners=True)
        self.up_sample2 = nn.Upsample(scale_factor=2, mode='trilinear', align_corners=True)
        
        self.dc1 = SSEConv2(128, 64, self.out_channel2, bias=self.bias, down_sample=4)
        self.dc2 = SSEConv2(64, 64, self.out_channel2, bias=self.bias,  down_sample=4)
        self.dc3 = SSEConv2(128, 64, self.out_channel2, bias=self.bias, down_sample=2)
        self.dc4 = SSEConv2(64, 32, self.out_channel2, bias=self.bias,  down_sample=2)
        self.dc5 = SSEConv(64, 32, self.out_channel2, bias=self.bias,  down_sample=1)
        self.dc6 = SSEConv(32, 16, self.out_channel2, bias=self.bias,  down_sample=1)
        

        self.dc0_0 = nn.Sequential(
                nn.Conv3d(24, n_classes, kernel_size=1, stride=1, padding=0, bias=self.bias))
        self.dc0_1 = nn.Sequential(
                nn.Conv3d(12, n_classes, kernel_size=1, stride=1, padding=0, bias=self.bias))

        self.dropout1 = droplayer(channel_num=24, thr=0.3)
        self.dropout2 = droplayer(channel_num=12, thr=0.3)

                
    def forward(self, x):
        e0, s0 = self.ec1(x)
        e1, s1 = self.ec2(e0)
        e1, s2 = self.ec3(e1) 
    
        e2 = self.pool0(e1)
        e2, s3 = self.ec4(e2)
        e3, s4 = self.ec5(e2)
        e3, s5 = self.ec6(e3)  

        e4 = self.pool1(e3)
        e4, s6 = self.ec7(e4) 
        e5, s7 = self.ec8(e4)
        e5, s8 = self.ec9(e5)
       
        e6 = self.pool2(e5)
        e6, s9 = self.ec10(e6)
        e7, s10 = self.ec11(e6) 
        e7, s11 = self.ec12(e7) 
        
        e8 = self.up_sample0(e7)
        d0, s12 = self.dc1(torch.cat((e8,e5),1))
        d0, s13 = self.dc2(d0)
        
        d1 = self.up_sample1(d0)
        d1, s14 = self.dc3(torch.cat((d1,e3),1))
        d1, s15 = self.dc4(d1)
        
        d2 = self.up_sample2(d1)
        d2, s16 = self.dc5(torch.cat((d2,e1),1))
        d2, s17 = self.dc6(d2)
        
        #output from the encoding group
        pred0 = self.dc0_0(self.dropout1(torch.cat((s0,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11),1)))
        #output from the decoding group
        pred1 = self.dc0_1(self.dropout2(torch.cat((s12,s13,s14,s15,s16,s17),1)))
     

        return pred0, pred1  
        
#------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='WingsNet Inference')
    parser.add_argument('-input', type=str, required=True, help='Path to the input folder')
    parser.add_argument('-output', type=str, required=True, help='Path to the output folder')
    args = parser.parse_args()

    input_folder = args.input
    output_folder = args.output

    #Get device
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print("Using GPU")
    else:
        device = torch.device("cpu")
        print("Using CPU")

    #Import model
    model = WingsNet()
    model.load_state_dict(torch.load('./models/ct/bronchi/wingsnet/wingsnet.ckpt')['state_dict'])
    model = model.to(device)
    model.eval()

    #Inference
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.startswith('.') or file.startswith('@'):
                continue
            if file.endswith(".nii.gz"):
                print("Processing file: ", file)
                
                file_path = os.path.join(root, file)

                # Create output folder in the same structure as the original folder tree
                current_output_folder = os.path.join(output_folder, os.path.relpath(root, input_folder))
                os.makedirs(current_output_folder, exist_ok=True)

                # Input file
                img = nib.load(file_path)
                data = img.get_fdata()
                input_data = torch.from_numpy(data).float()
                input_data = input_data.to(device)

                # Prediction
                #sliding window
                cube_size = 128
                step = 64

                pred = np.zeros(input_data.shape)
                pred_num = np.zeros(input_data.shape)
                xnum = (input_data.shape[0]-cube_size)//step + 1 if (input_data.shape[0]-cube_size)%step==0 else (input_data.shape[0]-cube_size)//step + 2
                ynum = (input_data.shape[1]-cube_size)//step + 1 if (input_data.shape[1]-cube_size)%step==0 else (input_data.shape[1]-cube_size)//step + 2
                znum = (input_data.shape[2]-cube_size)//step + 1 if (input_data.shape[2]-cube_size)%step==0 else (input_data.shape[2]-cube_size)//step + 2
                for xx in range(xnum):
                    xl = step*xx
                    xr = step*xx + cube_size
                    if xr > input_data.shape[0]:
                        xr = input_data.shape[0]
                        xl = input_data.shape[0]-cube_size
                    for yy in range(ynum):
                        yl = step*yy
                        yr = step*yy + cube_size
                        if yr > input_data.shape[1]:
                            yr = input_data.shape[1]
                            yl = input_data.shape[1] - cube_size
                        for zz in range(znum):
                            zl = step*zz
                            zr = step*zz + cube_size
                            if zr > input_data.shape[2]:
                                zr = input_data.shape[2]
                                zl = input_data.shape[2] - cube_size
                            
                            input_window = input_data[xl:xr, yl:yr, zl:zr].unsqueeze(0).unsqueeze(0)
                            _, p = model(input_window)
                            p = torch.sigmoid(p)
                            p = p.cpu().detach().numpy()
                            pred[xl:xr,yl:yr,zl:zr] += p.squeeze()
                            pred_num[xl:xr,yl:yr,zl:zr] += 1
                            
                pred = np.array(np.round(pred/pred_num), dtype=np.int8)
                pred = np.squeeze(pred)
                pred = np.where(pred > 0.5, 1, 0)

                # Save output file
                img.header.set_data_dtype(np.uint8)
                pred_nii = nib.Nifti1Image(pred, img.affine, img.header)
                nib.save(pred_nii, os.path.join(current_output_folder, file.split(".")[0]+ "_airway.nii.gz"))

    print("Inference completed")


if __name__ == '__main__':
    main()