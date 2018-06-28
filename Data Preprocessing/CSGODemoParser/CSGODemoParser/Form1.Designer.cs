namespace CSGODemoParser
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.txtResult = new System.Windows.Forms.TextBox();
            this.btnParser = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.txtInputFolder = new System.Windows.Forms.TextBox();
            this.txtOutputFolder = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.txtParserRoundNumber = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.cbShowDetailInfo = new System.Windows.Forms.CheckBox();
            this.SuspendLayout();
            // 
            // txtResult
            // 
            this.txtResult.Location = new System.Drawing.Point(12, 118);
            this.txtResult.Multiline = true;
            this.txtResult.Name = "txtResult";
            this.txtResult.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtResult.Size = new System.Drawing.Size(1163, 545);
            this.txtResult.TabIndex = 1;
            // 
            // btnParser
            // 
            this.btnParser.Location = new System.Drawing.Point(12, 23);
            this.btnParser.Name = "btnParser";
            this.btnParser.Size = new System.Drawing.Size(164, 74);
            this.btnParser.TabIndex = 2;
            this.btnParser.Text = "Parser Demos";
            this.btnParser.UseVisualStyleBackColor = true;
            this.btnParser.Click += new System.EventHandler(this.btnParser_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(199, 28);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(98, 18);
            this.label1.TabIndex = 3;
            this.label1.Text = "Demo Folder";
            // 
            // txtInputFolder
            // 
            this.txtInputFolder.Location = new System.Drawing.Point(301, 23);
            this.txtInputFolder.Name = "txtInputFolder";
            this.txtInputFolder.Size = new System.Drawing.Size(275, 29);
            this.txtInputFolder.TabIndex = 4;
            this.txtInputFolder.Text = "d:\\\\CSGOPlayer\\\\Raw\\\\";
            // 
            // txtOutputFolder
            // 
            this.txtOutputFolder.Location = new System.Drawing.Point(301, 61);
            this.txtOutputFolder.Name = "txtOutputFolder";
            this.txtOutputFolder.Size = new System.Drawing.Size(275, 29);
            this.txtOutputFolder.TabIndex = 6;
            this.txtOutputFolder.Text = "d:\\\\CSGOPlayer\\\\FirstOutput\\\\";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(196, 66);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(103, 18);
            this.label2.TabIndex = 5;
            this.label2.Text = "Output Folder";
            // 
            // txtParserRoundNumber
            // 
            this.txtParserRoundNumber.Location = new System.Drawing.Point(710, 23);
            this.txtParserRoundNumber.Name = "txtParserRoundNumber";
            this.txtParserRoundNumber.Size = new System.Drawing.Size(51, 29);
            this.txtParserRoundNumber.TabIndex = 8;
            this.txtParserRoundNumber.Text = "3";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(582, 28);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(126, 18);
            this.label3.TabIndex = 7;
            this.label3.Text = "ParserMaxRound";
            // 
            // cbShowDetailInfo
            // 
            this.cbShowDetailInfo.AutoSize = true;
            this.cbShowDetailInfo.Location = new System.Drawing.Point(585, 63);
            this.cbShowDetailInfo.Name = "cbShowDetailInfo";
            this.cbShowDetailInfo.Size = new System.Drawing.Size(201, 22);
            this.cbShowDetailInfo.TabIndex = 9;
            this.cbShowDetailInfo.Text = "Show Detail Parser Info";
            this.cbShowDetailInfo.UseVisualStyleBackColor = true;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 18F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1187, 699);
            this.Controls.Add(this.cbShowDetailInfo);
            this.Controls.Add(this.txtParserRoundNumber);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.txtOutputFolder);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.txtInputFolder);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.btnParser);
            this.Controls.Add(this.txtResult);
            this.Name = "Form1";
            this.Text = "Form1";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.TextBox txtResult;
        private System.Windows.Forms.Button btnParser;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox txtInputFolder;
        private System.Windows.Forms.TextBox txtOutputFolder;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox txtParserRoundNumber;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.CheckBox cbShowDetailInfo;
    }
}

