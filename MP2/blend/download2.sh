subjectlist=subjects.txt
while read -r subject;
do
    mkdir -p Func/$subject

    aws s3 cp \
        s3://hcp-openaccess/HCP_1200/$subject/MNINonLinear/Results/rfMRI_REST1_LR/rfMRI_REST1_LR_hp2000_clean.nii.gz \
        Func/$subject \
        --region us-east-1

    aws s3 cp \
        s3://hcp-openaccess/HCP_1200/$subject/MNINonLinear/Results/rfMRI_REST1_LR/rfMRI_REST1_LR.nii.gz \
        Func/$subject \
        --region us-east-1
    aws s3 cp \
        s3://hcp-openaccess/HCP_1200/$subject/MNINonLinear/Results/rfMRI_REST1_RL/rfMRI_REST1_RL.nii.gz \
        Func/$subject \
        --region us-east-1
    aws s3 cp \
        s3://hcp-openaccess/HCP_1200/$subject/MNINonLinear/Results/rfMRI_REST1_RL/rfMRI_REST1_RL_hp2000_clean.nii.gz \
        Func/$subject \
        --region us-east-1
    aws s3 cp \
        s3://hcp-openaccess/HCP_1200/$subject/MNINonLinear/Results/rfMRI_REST2_LR/rfMRI_REST2_LR.nii.gz \
        Func/$subject \
        --region us-east-1
    aws s3 cp \
        s3://hcp-openaccess/HCP_1200/$subject/MNINonLinear/Results/rfMRI_REST2_LR/rfMRI_REST2_LR_hp2000_clean.nii.gz \
        Func/$subject \
        --region us-east-1
    aws s3 cp \
        s3://hcp-openaccess/HCP_1200/$subject/MNINonLinear/Results/rfMRI_REST2_RL/rfMRI_REST2_RL.nii.gz \
        Func/$subject \
        --region us-east-1
    aws s3 cp \
        s3://hcp-openaccess/HCP_1200/$subject/MNINonLinear/Results/rfMRI_REST2_RL/rfMRI_REST2_RL_hp2000_clean.nii.gz \
        Func/$subject \
        --region us-east-1

done < $subjectlist