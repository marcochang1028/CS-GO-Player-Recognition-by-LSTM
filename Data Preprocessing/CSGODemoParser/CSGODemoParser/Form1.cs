using DemoInfo;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace CSGODemoParser
{
    /*
    Before read the code, I strongly suggest you to read the "CSGO Player Recognition by RNN (LSTM).pdf" 
    in the Doc folder first. This file can give you the overview of the whole research and some basic 
    knowledge about the CS:GO demo file and output file. All the comments below will assume that you have 
    read the document and had basic knowledge about this research.
    */
    public partial class Form1 : Form
    {
        private string folderName; // The folder put the Demo file
        private string outputFolderName; //The output folder 
        private DemoParser parser = null; 
        private bool isMatchStarted; //It will set to True in the beginning of parser procedure
        private bool isFreezetime; //It will set to false in the FreezetimeEnded event, and set to true in the RoundEnd event
        private bool showDetailInfo; //If it set to true, then the detailed parser info will be shown
        private int currentRoundNumber; //It will accumulate 1 in the RoundEnd event to keep the info of current round number
        private int stopRoundNumber; //For the test purpose, set to 3 to generate only first 3 rounds data. If you want to parse the whold rounds in the demo file, just simply set it to any number larger than 50
        private StreamWriter swMovement; //Write movement info into movement csv file
        private StringBuilder sbWeapon; //Write weapon Fired info into weapon csv file (even the knife swing action will be recorded)
        private StringBuilder sbHurt; //Write player hurt info into hurt csv file
        private StringBuilder sbNade; //Write grenade landing info into nade csv file

        public Form1()
        {
            InitializeComponent();
        }

        private void btnParser_Click(object sender, EventArgs e)
        {
            try
            {
                txtResult.Clear();

                folderName = txtInputFolder.Text;
                outputFolderName = txtOutputFolder.Text;

                if (Directory.Exists(folderName) && Directory.Exists(outputFolderName))
                {
                    string[] files = Directory.GetFiles(folderName, "*.dem", SearchOption.TopDirectoryOnly);

                    string fileNameWithoutExtension = "";
                    string fileName = "";

                    foreach (string file in files)
                    {
                        fileName = Path.GetFileName(file);
                        fileNameWithoutExtension = fileName.Substring(0, fileName.Length - 4);

                        outputFolderName = txtOutputFolder.Text + fileNameWithoutExtension + "\\";
                        
                        //If an folder with the same name as the currently processed file exists,
                        //then the current file is not processed.
                        if (Directory.Exists(outputFolderName))
                        {
                            txtResult.AppendText(fileName + " was parsered");
                            txtResult.AppendText(Environment.NewLine);
                            txtResult.AppendText(Environment.NewLine);
                        }
                        else
                        {
                            parser = new DemoParser(File.OpenRead(file));
                            RegisterEvents();
                            isMatchStarted = true;
                            isFreezetime = true;
                            showDetailInfo = cbShowDetailInfo.Checked;
                            stopRoundNumber = int.Parse(txtParserRoundNumber.Text);
                            currentRoundNumber = 1;

                            sbWeapon = new StringBuilder();
                            sbHurt = new StringBuilder();
                            sbNade = new StringBuilder();

                            Directory.CreateDirectory(outputFolderName);

                            txtResult.AppendText("======Strat Parser " + fileName + " at " + DateTime.Now + "======");
                            txtResult.AppendText(Environment.NewLine);

                            //As the movement data is hugh, we need to immediately write each record to the file to prevent this procedure run out the memory
                            using (swMovement = new StreamWriter(Path.Combine(outputFolderName, fileNameWithoutExtension + ".csv")))
                            {
                                
                                parser.ParseHeader();

                                txtResult.AppendText("ClientName: " + parser.Header.ClientName + ";  Map: " + parser.Header.MapName + ";  ServerName: " + parser.Header.ServerName);
                                txtResult.AppendText(Environment.NewLine);
                                txtResult.AppendText("PlaybackTicks: " + parser.Header.PlaybackTicks + ";  PlaybackTime: " + parser.Header.PlaybackTime + ";  TickRate: " + parser.TickRate + ";  TickTime: " + parser.TickTime);
                                txtResult.AppendText(Environment.NewLine);

                                parser.ParseToEnd();
                                parser.Dispose();
                            }
                            
                            File.WriteAllText(Path.Combine(outputFolderName, fileNameWithoutExtension + "-Weapon.csv"), sbWeapon.ToString());
                            File.WriteAllText(Path.Combine(outputFolderName, fileNameWithoutExtension + "-Hurt.csv"), sbHurt.ToString());
                            File.WriteAllText(Path.Combine(outputFolderName, fileNameWithoutExtension + "-Nade.csv"), sbNade.ToString());
                           
                            txtResult.AppendText(Environment.NewLine);
                            txtResult.AppendText("==============Parser Completed==============");
                            txtResult.AppendText(Environment.NewLine);
                            txtResult.AppendText(Environment.NewLine);
                        }
                    }
                }
                else
                {
                    txtResult.AppendText("Folder is not exist.");
                    txtResult.AppendText(Environment.NewLine);

                }
            }
            catch (Exception ex)
            {
                txtResult.AppendText(ex.ToString());

            }

        }

        private void ParserHeader(string folderName, string fileName)
        {
            DateTime dateFile = File.GetCreationTime(folderName + fileName);

            txtResult.AppendText("=======Start Parser " + fileName + " at " + DateTime.Now + "=============");
            txtResult.AppendText(Environment.NewLine);

            try
            {
                parser.ParseHeader();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Exception:" + ex.ToString());
            }

            DemoHeader header = parser.Header;
            FileInfo fi = new FileInfo(folderName + fileName);
            int seconds = (int)fi.LastWriteTime.Subtract(new DateTime(1970, 1, 1)).TotalSeconds;
            txtResult.AppendText(header.MapName.Replace("/", "") + "_" + header.SignonLength + header.PlaybackTicks + header.PlaybackFrames + seconds + fi.Length);
            txtResult.AppendText(Environment.NewLine);
            txtResult.AppendText("Client name: " + header.ClientName);
            txtResult.AppendText(Environment.NewLine);
            txtResult.AppendText("Server name: " + header.ServerName);
            txtResult.AppendText(Environment.NewLine);
            if (header.PlaybackTicks != 0 && header.PlaybackTime != 0)
            {
                txtResult.AppendText(("Tick Rate: " + header.PlaybackTicks / header.PlaybackTime).ToString());
                txtResult.AppendText(Environment.NewLine);
            }
            else
            {
                txtResult.AppendText("corrupted");
                txtResult.AppendText(Environment.NewLine);
            }
            if (header.PlaybackFrames != 0 && header.PlaybackTime != 0)
            {
                //Tick rate
                txtResult.AppendText("Tick Rate: " + ((int)Math.Round((double)header.PlaybackFrames / header.PlaybackTime)).ToString());
                txtResult.AppendText(Environment.NewLine);
            }


            txtResult.AppendText("Playback time: " + header.PlaybackTime.ToString()); //Duration
            txtResult.AppendText(Environment.NewLine);
            txtResult.AppendText("Map name: " + header.MapName);
            txtResult.AppendText(Environment.NewLine);
            txtResult.AppendText("Playback tick: " + header.PlaybackTicks.ToString());
            txtResult.AppendText(Environment.NewLine);
        }

        private void RegisterEvents()
        {
            /*
             * I list all the events here for your reference,
             * but I only commented the events we used in the program
             */
            //parser.PlayerTeam += HandlePlayerTeam;
            //parser.MatchStarted += HandleMatchStarted;
            //parser.RoundStart += HandleRoundStart;
            parser.FreezetimeEnded += HandleFreezetimeEnded; //It is only occured once when a round start
            parser.TickDone += HandleTickDone; // It is occured in the end of every ticks
            parser.WeaponFired += HandleWeaponFired; // It is occured in the end of a weapon fired by a player (includes shooting, nade throwing, knife swing) 
            parser.PlayerHurt += HandlePlayerHurted; // It is occured after a player is hurt by any reason (even he jumped from a very high place to the ground and hurt himself)
            //parser.PlayerKilled += HandlePlayerKilled;
            parser.FlashNadeExploded += HandleFlashNadeExploded; // It is occured when a flash nade lands on the ground
            parser.ExplosiveNadeExploded += HandleExplosiveNadeExploded;  // It is occured when a explosive nade lands on the ground
            parser.SmokeNadeStarted += HandleSmokeNadeStarted; // It is occured when a smoke nade lands on the ground
            //parser.SmokeNadeEnded += HandleSmokeNadeEnded;
            parser.FireNadeStarted += HandleFireNadeStarted; // It is occured when a fire nade lands on the ground
            //parser.FireNadeEnded += HandleFireNadeEnded;
            parser.DecoyNadeStarted += HandleDecoyNadeStarted; // // It is occured when a decoy nade lands on the ground
            //parser.DecoyNadeEnded += HandleDecoyNadeEnded;
            //parser.BombPlanted += HandleBombPlanted;
            //parser.BombDefused += HandleBombDefused;
            //parser.BombExploded += HandleBombExploded;
            parser.RoundEnd += HandleRoundEnd; //It is only occured once when a round end
            //parser.RoundMVP += HandleRoundMvp;
            //parser.RoundOfficiallyEnd += HandleRoundOfficiallyEnd;
            //parser.WinPanelMatch += HandleWinPanelMatch;
            //parser.LastRoundHalf += HandleLastRoundHalf;
            //parser.SayText += HandleSayText;
            //parser.SayText2 += HandleSayText2;
            //parser.PlayerDisconnect += HandlePlayerDisconnect;
        }

        protected void HandleFreezetimeEnded(object sender, FreezetimeEndedEventArgs e)
        {
            
            if (!isMatchStarted) return;

            isFreezetime = false;

            if (showDetailInfo)
            {
                txtResult.AppendText("The Freeze Time is end and the tick is " + parser.IngameTick);
                txtResult.AppendText(Environment.NewLine);

                foreach (Player player in parser.PlayingParticipants)
                {
                    txtResult.AppendText("Player equipments after the freeze time; " + parser.CurrentTick + "; " + parser.CurrentTime + "; " + currentRoundNumber.ToString() + "; " + parser.Map);
                    txtResult.AppendText("; " + player.SteamID + "; " + player.Name);

                    foreach (Equipment weapon in player.Weapons)
                    {
                        txtResult.AppendText("; " + weapon.Weapon.ToString() + ",");
                    }

                    txtResult.AppendText(Environment.NewLine);

                }

            }



        }

        protected void HandleTickDone(object sender, TickDoneEventArgs e)
        {
            if (!isMatchStarted || isFreezetime || currentRoundNumber > stopRoundNumber) return;

            if (showDetailInfo)
            {
                if (parser.CurrentTick % 5000 == 0)
                {
                    txtResult.AppendText("Parser progress:" + parser.CurrentTick + " / " + parser.Header.PlaybackTicks);
                    txtResult.AppendText(Environment.NewLine);
                }
            }

            int activeWeapon = -1;

            if (parser.PlayingParticipants.Any())
            {
                foreach (Player player in parser.PlayingParticipants)
                {
                    
                    if (player.IsAlive)
                    {
                        if (player.ActiveWeapon != null)
                            activeWeapon = (int)player.ActiveWeapon.Weapon;

                        swMovement.WriteLine(parser.CurrentTick + "," + currentRoundNumber.ToString() + "," + parser.Map + "," + player.SteamID + "," + player.Name + "," + (int)player.Team + "," + player.Position.X + "," + player.Position.Y + "," + player.Position.Z + "," + player.Velocity.X + "," + player.Velocity.Y + "," + player.Velocity.Z + "," + player.ViewDirectionX + "," + player.ViewDirectionY + "," + activeWeapon + "," + (int)ActionEnum.Movement + ",0,0,0,0");
                    }

                }

            }
        }

        protected void HandleWeaponFired(object sender, WeaponFiredEventArgs e)
        {
            if (!isMatchStarted || e.Shooter == null || e.Weapon == null || currentRoundNumber > stopRoundNumber) return;

            sbWeapon.AppendLine(parser.CurrentTick + "," + e.Shooter.SteamID + "," + e.Shooter.Name + "," + (int)e.Weapon.Weapon + "," + (int)ActionEnum.Fired);
        }

        protected void HandlePlayerHurted(object sender, PlayerHurtEventArgs e)
        {
            if (!isMatchStarted || e.Player == null || e.Weapon == null || e.Attacker == null || currentRoundNumber > stopRoundNumber) return;

            ActionEnum actionEnum;

            if ((int)e.Weapon.Weapon <= 500)
                actionEnum = ActionEnum.HurtNotByNade;
            else
                actionEnum = ActionEnum.HurtByNade;

            sbHurt.AppendLine(parser.CurrentTick + "," + e.Attacker.SteamID + "," + e.Attacker.Name + "," + (int)e.Weapon.Weapon + "," + (int)actionEnum + "," + (int)e.Hitgroup + "," + e.Player.Position.X + "," + e.Player.Position.Y + "," + e.Player.Position.Z);            
        }

        protected void HandleFlashNadeExploded(object sender, FlashEventArgs e)
        {
            if (!isMatchStarted || e.ThrownBy == null || currentRoundNumber > stopRoundNumber) return;

            sbNade.AppendLine(parser.CurrentTick + "," + e.ThrownBy.SteamID + "," + e.ThrownBy.Name + "," + (int)e.NadeType + "," + (int)ActionEnum.HurtByNade + "," + e.Position.X + "," + e.Position.Y + "," + e.Position.Z);
        }

        protected void HandleExplosiveNadeExploded(object sender, GrenadeEventArgs e)
        {
            if (!isMatchStarted || e.ThrownBy == null || currentRoundNumber > stopRoundNumber) return;

            sbNade.AppendLine(parser.CurrentTick + "," + e.ThrownBy.SteamID + "," + e.ThrownBy.Name + "," + (int)e.NadeType + "," + (int)ActionEnum.HurtByNade + "," + e.Position.X + "," + e.Position.Y + "," + e.Position.Z);
        }

        protected void HandleSmokeNadeStarted(object sender, SmokeEventArgs e)
        {
            if (!isMatchStarted || e.ThrownBy == null || currentRoundNumber > stopRoundNumber) return;

            sbNade.AppendLine(parser.CurrentTick + "," + e.ThrownBy.SteamID + "," + e.ThrownBy.Name + "," + (int)e.NadeType + "," + (int)ActionEnum.HurtByNade + "," + e.Position.X + "," + e.Position.Y + "," + e.Position.Z);
        }

        protected void HandleFireNadeStarted(object sender, FireEventArgs e)
        {
            if (!isMatchStarted || e.ThrownBy == null || currentRoundNumber > stopRoundNumber) return;

            sbNade.AppendLine(parser.CurrentTick + "," + e.ThrownBy.SteamID + "," + e.ThrownBy.Name + "," + (int)e.NadeType + "," + (int)ActionEnum.HurtByNade + "," + e.Position.X + "," + e.Position.Y + "," + e.Position.Z);
        }

        protected void HandleDecoyNadeStarted(object sender, DecoyEventArgs e)
        {
            if (!isMatchStarted || e.ThrownBy == null || currentRoundNumber > stopRoundNumber) return;

            sbNade.AppendLine(parser.CurrentTick + "," + e.ThrownBy.SteamID + "," + e.ThrownBy.Name + "," + (int)e.NadeType + "," + (int)ActionEnum.HurtByNade + "," + e.Position.X + "," + e.Position.Y + "," + e.Position.Z);
        }

        protected void HandleRoundEnd(object sender, RoundEndedEventArgs e)
        {
            if (!isMatchStarted || isFreezetime) return;

            isFreezetime = true;
            txtResult.AppendText("Round " + currentRoundNumber.ToString() + ": " + parser.IngameTick + "; ");

            if (showDetailInfo)
            {
                txtResult.AppendText(Environment.NewLine);

                foreach (Player player in parser.PlayingParticipants)
                {
                    txtResult.AppendText("Player equipments at the round end; " + parser.CurrentTick + "; " + parser.CurrentTime + "; " + currentRoundNumber.ToString() + "; " + parser.Map);
                    txtResult.AppendText("; " + player.SteamID + "; " + player.Name);

                    foreach (Equipment weapon in player.Weapons)
                    {
                        txtResult.AppendText("; " + weapon.Weapon.ToString() + ",");
                    }

                    txtResult.AppendText(Environment.NewLine);
                }
            }

            currentRoundNumber += 1;
        }

        private enum ActionEnum
        {
            Movement = 0,
            Fired = 1,
            HurtNotByNade = 2,
            HurtByNade = 3,
        }
    }
}
